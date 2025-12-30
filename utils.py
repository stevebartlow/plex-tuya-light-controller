from colorthief import ColorThief
import io
import requests

def get_dominant_color(image_url, temp_file_path='temp_poster.jpg'):
    """
    Downloads an image from a URL and extracts the dominant color.
    Returns: (r, g, b) tuple or None if failed.
    """
    try:
        # Note: In a real scenario with Plex, we might need headers (Token)
        # But this function just takes the URL or file-like object
        # Since ColorThief handles files best, we might download to a temp buffer
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            
            color_thief = ColorThief(temp_file_path)
            # get_color(quality=1) is the highest quality
            dominant_color = color_thief.get_color(quality=10)
            return dominant_color
    except Exception as e:
        print(f"Error extracting color: {e}")
        return None

def get_dominant_color_from_bytes(image_bytes):
    """
    Extracts dominant color directly from image bytes.
    """
    try:
        f = io.BytesIO(image_bytes)
        color_thief = ColorThief(f)
        return color_thief.get_color(quality=10)
    except Exception as e:
        print(f"Error extracting color from bytes: {e}")
        return None
