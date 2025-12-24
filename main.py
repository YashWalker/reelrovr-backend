from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.extractor import extract_media_info
from utils.validators import validate_instagram_url, sanitize_url
import requests

# Mimic Instagram Android App to avoid 403/Hotlinking issues
HEADERS = {
    "User-Agent": "Instagram 219.0.0.12.117 Android (31/12; 320dpi; 720x1280; samsung; SM-A325F; a32; qcom; en_US; 314665256)",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

app = FastAPI(title="ReelRovr API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to ReelRovr API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/extract")
def extract_media(request: URLRequest):
    url = request.url
    if not validate_instagram_url(url):
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")
    
    clean_url = sanitize_url(url)
    try:
        data = extract_media_info(clean_url)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
def download_media(url: str):
    """
    Proxies the download to avoid CORS and headers issues.
    """
    try:
        # Stream the content with custom headers
        r = requests.get(url, stream=True, headers=HEADERS)
        r.raise_for_status()
        
        # Forward headers if needed (content-type, content-length)
        return Response(
            content=r.content,
            media_type=r.headers.get("Content-Type"),
            headers={
                "Content-Disposition": f"attachment; filename=download"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to download media")

@app.get("/api/proxy")
def proxy_media(url: str):
    """
    Proxies image requests to bypass hotlinking protection/CORS.
    """
    try:
        r = requests.get(url, stream=True, headers=HEADERS)
        r.raise_for_status()
        return Response(content=r.content, media_type=r.headers.get("Content-Type"))
    except Exception:
        # Return a fallback 404 or generic error image if needed, but for now just fail.
        raise HTTPException(status_code=404, detail="Image not found")
