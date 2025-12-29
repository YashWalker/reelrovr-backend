import instaloader
import os
import re
import base64
from typing import Dict, Any

def extract_media_info(url: str) -> Dict[str, Any]:
    """
    Extracts media information from an Instagram URL using Instaloader.
    Returns structured media info for reels, carousels, or image posts.
    """
    
    # 1. Configure Instaloader
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 2. Load Cookies
    cookies_content = os.getenv("INSTAGRAM_COOKIES")
    if cookies_content:
        try:
            # Base64 Decode
            if not cookies_content.strip().startswith("# Netscape"):
                decoded = base64.b64decode(cookies_content).decode('utf-8')
                if "# Netscape" in decoded:
                    cookies_content = decoded
                    print("DEBUG: Base64 cookies decoded")
        except Exception:
            pass

        # Fix newlines
        if "\\n" in cookies_content and "\n" not in cookies_content:
            cookies_content = cookies_content.replace("\\n", "\n")

        # Parse Netscape cookies
        cookies = {}
        for line in cookies_content.splitlines():
            if line.strip().startswith("#") or not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 7:
                 # domain, flag, path, secure, expiration, name, value
                cookies[parts[5]] = parts[6]
        
        # Load into context
        L.context._session.cookies.update(cookies)
        print(f"DEBUG: Loaded {len(cookies)} cookies into Instaloader.")

    # 3. Extract Shortcode
    shortcode_match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', url)
    if not shortcode_match:
        raise Exception("Invalid Instagram URL. Could not find shortcode.")
    shortcode = shortcode_match.group(1)
    
    print(f"DEBUG: Fetching post shortcode: {shortcode}")

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        print(f"DEBUG: Post fetch success. Type: {post.typename}")
        
        media_list = []
        is_sidecar = (post.typename == 'GraphSidecar')

        # Helper to format response item
        def format_node(node, is_video_override=None):
            # Check logical type
            is_vid = node.is_video if is_video_override is None else is_video_override
            
            # Safe access to display_url (Post uses .url, SidecarNode uses .display_url)
            display_url = getattr(node, 'display_url', getattr(node, 'url', None))
            
            # Instaloader 'video_url' can be None if it's an image
            url = node.video_url if is_vid else display_url
            
            # Fallback if video_url missing but is_video says yes (rare edge case or restricted)
            if is_vid and not url:
                if display_url:
                    # Fallback to image
                    is_vid = False
                    url = display_url
            
            return {
                "type": "video" if is_vid else "image",
                "url": url,
                "thumbnail": display_url, 
                "width": 0,
                "height": 0,
                # Placeholder filename, will be updated in loop with index
                "filename": f"{shortcode}.{'mp4' if is_vid else 'jpg'}" 
            }

        if is_sidecar:
            # We iterate nodes
            print(f"DEBUG: Processing {post.mediacount} sidecar nodes...")
            for i, node in enumerate(post.get_sidecar_nodes()):
                item = format_node(node)
                # Update filename with index
                ext = 'mp4' if item['type'] == 'video' else 'jpg'
                item['filename'] = f"{shortcode}_{i+1}.{ext}"
                media_list.append(item)
            
            # Fallback for sidecars that look empty (restricted children)
            if not media_list and post.url:
                 print("DEBUG: No sidecar nodes extracted. Falling back to main post image.")
                 media_list.append({
                     "type": "image",
                     "url": post.url,
                     "thumbnail": post.url,
                     "width": 0,
                     "height": 0,
                     "filename": f"{shortcode}.jpg"
                 })
        else:
            # Single Post / Reel
            item = format_node(post)
            # Filename is already set to shortcode.ext in helper
            media_list.append(item)

        if not media_list:
            raise Exception("No media found (empty list).")

        return {
            "id": post.shortcode,
            "title": "Instagram Post",
            "description": post.caption,
            "thumbnail": post.url,
            "is_sidecar": is_sidecar,
            "media": media_list
        }

    except Exception as e:
        error_str = str(e)
        if "403" in error_str or "Login" in error_str:
             print(f"DEBUG: Instaloader 403/Login Error: {e}")
             raise Exception("Access Denied: Please check your cookies. Instagram is blocking the request.")
        raise Exception(f"Extraction failed: {error_str}")
