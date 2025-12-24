import re

def validate_instagram_url(url: str) -> bool:
    """
    Validates if the provided URL is a valid Instagram URL.
    Supports Posts, Reels, and TV.
    """
    pattern = r"https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel|tv)\/([a-zA-Z0-9_-]+)\/?"
    return bool(re.match(pattern, url))

def sanitize_url(url: str) -> str:
    """
    Removes query parameters from the Instagram URL to get the clean direct link.
    """
    if "?" in url:
        return url.split("?")[0]
    return url
