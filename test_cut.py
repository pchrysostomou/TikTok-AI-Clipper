import sys
sys.path.append('backend/services')
from downloader import download_clip_segment
try:
    print("Testing video cut...")
    # 2-second cut from a known video (e.g., Me at the zoo)
    download_clip_segment('https://www.youtube.com/watch?v=jNQXAC9IVRw', 5.0, 7.0, 'test_clip.mp4')
    print("Success")
except Exception as e:
    print(f"Error: {e}")
