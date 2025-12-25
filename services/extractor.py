import yt_dlp
from typing import Dict, Any

def extract_media_info(url: str) -> Dict[str, Any]:
    """
    Extracts media information from an Instagram URL using yt-dlp.
    Returns a dictionary with title, thumbnail, and download URL.
    """
    # Support for cookies via environment variable (for blocked server IPs)
    import os
    import tempfile
    
    # Support for cookies via environment variable (for blocked server IPs)
    import os
    import tempfile
    
    cookie_file = None
    cookies_content = os.getenv("INSTAGRAM_COOKIES")
    
    if cookies_content:
        # Common fix: valid netscape cookies need newlines, but env vars often flatten them.
        # Check if we need to restore newlines
        if "\\n" in cookies_content and "\n" not in cookies_content:
            print("DEBUG: Detected escaped newlines in cookie variable. Restoring...")
            cookies_content = cookies_content.replace("\\n", "\n")

        line_count = len(cookies_content.splitlines())
        print(f"DEBUG: Found cookies content (Length: {len(cookies_content)}, Lines: {line_count})")
        
        if not cookies_content.strip().startswith("# Netscape"):
            print("WARNING: Cookies header missing! First 50 chars:", cookies_content[:50])
        
    else:
        print("DEBUG: No INSTAGRAM_COOKIES environment variable found.")

    ydl_opts = {
        'parse_metadata': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'cachedir': False, # Disable cache to prevent stale errors
    }

    if cookies_content:
        # Create a temporary file for cookies
        try:
            fd, cookie_file = tempfile.mkstemp(suffix='.txt', text=True)
            with os.fdopen(fd, 'w') as f:
                f.write(cookies_content)
            ydl_opts['cookiefile'] = cookie_file
            print(f"DEBUG: Wrote cookies to temp file: {cookie_file}")
        except Exception as e:
            print(f"ERROR: Failed to write cookie file: {e}")
    
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
        finally:
            # Cleanup cookie file
            if cookie_file and os.path.exists(cookie_file):
                try:
                    os.unlink(cookie_file)
                except:
                    pass
