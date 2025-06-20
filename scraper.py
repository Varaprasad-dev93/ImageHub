from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
import requests

def is_scraping_allowed(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        res = requests.get(robots_url, timeout=5)
        if "Disallow: /" in res.text:
            return False
        return True
    except:
        return True  # Assume allowed if robots.txt is unreachable

def get_internal_links(base_url, html):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return links

def download_image(img_url, folder_path, count):
    try:
        img_data = requests.get(img_url, timeout=5).content
        ext = os.path.splitext(urlparse(img_url).path)[1][:5] or ".png"
        filename = os.path.join(folder_path, f"image_{count+1}{ext}")
        with open(filename, 'wb') as f:
            f.write(img_data)
        return True
    except:
        return False

async def scrape_images(url: str, max_images: int = 10, allowed_types: list[str] = None):
    visited = set()
    to_visit = [url]
    count = 0
    img_urls = []

    # Normalize allowed_types to include dot prefix
    if allowed_types:
        allowed_types = [ext.lower().strip().lstrip(".") for ext in allowed_types]
    else:
        # Fallback: accept common types if not specified
        allowed_types = ["jpg", "jpeg", "png", "gif", "webp"]

    while to_visit and count < max_images:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            })
            response = session.get(current_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Download images on this page
            img_tags = soup.find_all("img")
            for img in img_tags:
                if count >= max_images:
                    break
                img_url = img.get("src")
                if img_url:
                    full_img_url = urljoin(current_url, img_url)
                    ext = full_img_url.split(".")[-1].split("?")[0].lower()

                    if ext in allowed_types:
                        img_urls.append(full_img_url)
                        count = len(img_urls)

            # Find internal links to continue crawling
            internal_links = get_internal_links(current_url, response.text)
            for link in internal_links:
                if link not in visited and len(to_visit) < 50:
                    to_visit.append(link)

        except Exception:
            continue

    return img_urls