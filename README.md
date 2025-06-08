# 🧙‍♂️ AI Mage Hub — Backend

**AI Mage Hub** is an intelligent backend service that allows users to:
- 🔍 Scrape images from any website (with permission),
- 🎯 Filter and download specific image ranges,
- 🖼️ Generate images from text using AI (Together.ai),
- 💬 Chat with the AI to get creative prompt ideas,
- ⏳ Allow one-time ZIP download before auto-cleanup.

Built with **FastAPI**, this backend powers the core functionality of the AI Mage Hub platform.

---

## 🚀 Features

- ✅ Scrape images from any valid public webpage
- 🧠 AI image generation using [Together.ai](https://www.together.ai/)
- 🔒 One-time download with auto-deletion for security
- 📁 Image compression and ZIP creation
- ⏱ Background cleanup using APScheduler
- 🔗 Prompt suggestions and chat-based generation (optional)
- 🌐 CORS enabled for frontend integration (e.g., React/Next.js)

---

## 📦 Tech Stack

- **Backend Framework:** FastAPI (Python)
- **Scheduler:** APScheduler
- **AI API:** Together.ai Text-to-Image
- **Web Scraping:** `requests`, `BeautifulSoup`
- **Environment Management:** Python `dotenv`
- **Image Processing:** PIL, `shutil`, `uuid`
- **CORS Support:** `fastapi.middleware.cors`

---

## 🛠️ Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/your-username/ai-mage-hub-backend.git
cd ai-mage-hub-backend
"# ImageHub"


##Create a Virtual Environment & Install Dependencies:

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt


##Set Up Environment Variables:

TOGETHER_API_KEY=your_together_ai_api_key_here


##Run the Server:

uvicorn main:app --reload

##🔌 API Endpoints
📷 /scrape
Scrapes images from a website and returns valid image URLs.

Method: POST

Payload:

{
  "url": "https://example.com",
  "max_images": 5 -50 (default :10)
}
🖼️ /generate
Generates images from a prompt using Together.ai.

Method: POST

Payload:

{
  "prompts": ["sunset over the ocean", "futuristic city skyline"]
}
📥 /download/{token}
Downloads a ZIP file of scraped/generated images. This is a one-time-use download link.

##🧹 Background Auto-Cleanup
Images and ZIP files are automatically deleted after a scheduled interval (default: every 15 minutes). This is managed by apscheduler.

⚙️ Configuration Options
You can customize the following settings inside main.py or .env:

Max number of images scraped
File cleanup interval
Together.ai API key

🧪 Sample .env

TOGETHER_API_KEY=abcdef1234567890
DELETE_INTERVAL_SECONDS=900


📁 Folder Structure

ai-mage-hub-backend/
│
├── main.py               # FastAPI app and routes
├── scraper.py            # Image scraping logic
├── generate_utils.py     # AI generation logic with Together.ai
├── .env                  # API keys and settings
├── requirements.txt      # Python dependencies
└── temp/                 # Temporary image and zip storage


##📋 To-Do / Roadmap
 Add user authentication (optional)

 Limit prompt requests per user (rate limiting)

 Store image generation history

 Support other AI APIs (Replicate, Stability AI)


##🙌 Acknowledgments
Together.ai

FastAPI

BeautifulSoup
