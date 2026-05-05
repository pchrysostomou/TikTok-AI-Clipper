import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _build_client(access_token: str, refresh_token: str = ""):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token or None,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def upload_youtube_short(
    video_path: str,
    title: str,
    description: str,
    access_token: str,
    refresh_token: str = "",
) -> dict:
    """Upload a video to YouTube as a Short and return video_id + URL."""
    try:
        youtube = _build_client(access_token, refresh_token)

        body = {
            "snippet": {
                "title": title[:100],
                "description": f"{description}\n\n#Shorts #AI #Viral",
                "tags": ["Shorts", "AI", "viral", "clips"],
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024 * 1024)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"YouTube upload: {int(status.progress() * 100)}%")

        video_id = response["id"]
        url = f"https://www.youtube.com/shorts/{video_id}"
        logger.info(f"YouTube Short uploaded: {url}")
        return {"video_id": video_id, "url": url}

    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        raise RuntimeError(f"YouTube upload failed: {e}")
