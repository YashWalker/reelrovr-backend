import yt_dlp
from typing import Dict, Any

def extract_media_info(url: str) -> Dict[str, Any]:
    """
    Extracts media information from an Instagram URL using yt-dlp.
    Returns a dictionary with title, thumbnail, and download URL.
    """
    ydl_opts = {
        'parse_metadata': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True, # Fix for SSL errors on work laptops/proxies
        'ignoreerrors': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                 raise Exception("No info returned")
                 
            return {
                "id": info.get("id"),
                "title": info.get("title", "Instagram Media"),
                "thumbnail": info.get("thumbnail"),
                "url": info.get("url"),
                "ext": info.get("ext"),
                "is_video": info.get("ext") == "mp4"
            }
        except Exception as e:
            # Strip ANSI color codes from yt-dlp errors
            import re
            error_msg = re.sub(r'\x1b\[[0-9;]*m', '', str(e))
            raise Exception(f"Failed to extract media: {error_msg}")
