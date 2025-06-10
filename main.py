from fastapi import FastAPI, HTTPException, Form, Request, Response
import uuid,os,shutil,time
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import scrape_images
from generate_utils import generate_multiple_images  # adjust this if needed
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
from urllib.parse import urljoin
import uvicorn
import httpx
import asyncio
load_dotenv()

TEMP_DIR = "temp"
ZIP_DIR = "temp_zips"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ZIP_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI()
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
# Add your frontend URL here
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://192.168.32.33:8080",
    "http://0.0.0.0:8080",
]
# Add CORS middleware to allow requests from the frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Or use ["*"] to allow all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)


def get_base_url(request: Request) -> str:
    
    if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:  # Render.com
        return f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}"
    if 'VERCEL_URL' in os.environ:  # Vercel
        return f"https://{os.environ['VERCEL_URL']}"
    
    # Fallback to request-based detection
    return str(request.base_url).rstrip('/')



# Cleanup helper: removes zip and image folder
def cleanup_files(zip_path: str, folder_path: str):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

def periodic_cleanup():
    now = time.time()
    expiry_seconds = 5 * 60  # 5 minutes

    def remove_old_files(directory):
        for folder in os.listdir(directory):
            folder_path = os.path.join(directory, folder)
            if os.path.isdir(folder_path):
                folder_time = os.path.getmtime(folder_path)
                if now - folder_time > expiry_seconds:
                    shutil.rmtree(folder_path)
                    print(f"🧹 Removed old folder: {folder_path}")
            elif os.path.isfile(folder_path):
                file_time = os.path.getmtime(folder_path)
                if now - file_time > expiry_seconds:
                    os.remove(folder_path)
                    print(f"🧹 Removed old file: {folder_path}")

    remove_old_files(TEMP_DIR)
    remove_old_files(ZIP_DIR)

# Start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(periodic_cleanup, "interval", minutes=5)
scheduler.start()

from threading import Lock
count_lock = Lock()
count = 0

@app.get("/")
async def root():
    return {"message": "App is running"}

def increment_visit_count() -> int:
    """Thread-safe visit counter increment"""
    with count_lock:
        
        # Read-modify-write in a single operation
        with open("Visits.txt", 'r+') as f:
            try:
                count = int(f.read().strip() or 0)
            except ValueError:
                count = 0
            print(f"Current visit count: {count}")
            print("File opened successfully",f)
            count += 1
            f.seek(0)
            f.truncate()
            f.write(str(count))
            
        return count
    
    
@app.get("/visit")
async def visit_tracker(request: Request, response: Response):
    global count, count_lock
    count = increment_visit_count()
    response.set_cookie(
        key="visited",
        value="true",
        max_age=31536000,
        httponly=True,
        samesite="Lax",
        secure=True,
    )
    return {"count": count}

@app.post("/api/scrape")
async def handle_scrape(url:str = Form(...), max_images: int = Form(...)):
    present=time.time()
    
    try:
        # print(f"Starting scraping for {url} with max_images={max_images}")
        imgUrls = await scrape_images(url,  max_images)

        if not imgUrls:
            raise HTTPException(status_code=404, detail="No images found at the provided URL.")
        # print(f"Scarping takes {time.time()-present} seconds")
        return {
            "message": f"Scraping completed for {url}. Found {len(imgUrls)} images.",
            "images_link": imgUrls
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")

@app.post("/api/generate-image")
async def generate_images(prompt: str = Form(...),number: int = Form(5)):
    start_time = time.time()
    image_paths=[]
    try:
        # Generate 5 images (adjust if needed)
        image_paths=generate_multiple_images(prompt, image_paths,number)
        if not image_paths:
            raise HTTPException(status_code=500, detail="Image generation failed or returned no images.")

        elapsed = time.time() - start_time
        # print(f"Image generation for '{prompt}' completed in {elapsed:.2f} seconds.")

        return {
            "message": f"{number} images generated for prompt: {prompt}",
            "images_link": image_paths
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

async def save_image(url):
    try:
        filename = uuid.uuid4().hex[:6] + ".png"
        path = os.path.join(TEMP_DIR, filename)

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
                return path
            else:
                raise Exception(f"Failed to download image, status: {response.status_code}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None  
 

            
@app.post("/api/download")
async def download_images(request: Request):
    form = await request.form()
    token_list = form.getlist("token")
    
    if not token_list:
        raise HTTPException(status_code=400, detail="No image tokens provided")
    
    try:
        # Process all downloads concurrently
        tasks = [save_image(url) for url in token_list]
        results = await asyncio.gather(*tasks)
        
        # Generate URLs for successfully downloaded files
        downloaded_urls = [
            urljoin(
                str(get_base_url(request)),
                Path(filename).as_posix()
            )
            for filename in results 
            if filename  # Only include successful downloads
        ]
        
        return JSONResponse(content=downloaded_urls)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download processing failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
