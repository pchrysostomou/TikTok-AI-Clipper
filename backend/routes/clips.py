from fastapi import APIRouter, HTTPException, Query
from database import get_db
from models import PublishYouTubeRequest
from services.publisher import upload_youtube_short
import cloudinary.uploader
import logging, tempfile, httpx, os

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/clips")
async def get_clips(user_id: str = Query(...)):
    try:
        r = get_db().table("clips").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return r.data
    except Exception as e:
        logger.warning(f"DB error fetching clips: {e}")
        return []


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        r = get_db().table("processing_jobs").select("*").eq("id", job_id).execute()
        if not r.data:
            raise HTTPException(404, "Job not found")
        return r.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"DB error fetching job: {e}")
        raise HTTPException(500, "Database not ready. Run the Supabase schema first.")


@router.delete("/clips/{clip_id}")
async def delete_clip(clip_id: str, user_id: str = Query(...)):
    db = get_db()
    r = db.table("clips").select("cloudinary_public_id").eq("id", clip_id).eq("user_id", user_id).execute()
    if not r.data:
        raise HTTPException(404, "Clip not found")

    pub_id = r.data[0].get("cloudinary_public_id")
    if pub_id:
        try:
            cloudinary.uploader.destroy(pub_id, resource_type="video")
        except Exception as e:
            logger.warning(f"Cloudinary delete failed: {e}")

    db.table("clips").delete().eq("id", clip_id).execute()
    return {"success": True}


@router.post("/clips/{clip_id}/publish/youtube")
async def publish_to_youtube(clip_id: str, req: PublishYouTubeRequest):
    db = get_db()

    # Get clip
    clip_r = db.table("clips").select("*").eq("id", clip_id).execute()
    if not clip_r.data:
        raise HTTPException(404, "Clip not found")
    clip = clip_r.data[0]

    # Get YouTube tokens
    acc_r = db.table("connected_accounts").select("*").eq("user_id", req.user_id).eq("platform", "youtube").execute()
    if not acc_r.data:
        raise HTTPException(400, "YouTube account not connected. Go to /connect first.")
    acc = acc_r.data[0]

    # Download clip from Cloudinary
    with tempfile.TemporaryDirectory() as tmp:
        video_path = f"{tmp}/clip.mp4"
        async with httpx.AsyncClient(timeout=60) as client:
            video_r = await client.get(clip["cloudinary_url"])
        with open(video_path, "wb") as f:
            f.write(video_r.content)

        caption = req.caption or clip["title"]
        result = upload_youtube_short(
            video_path=video_path,
            title=caption,
            description=f"AI-generated clip\n\nOriginal: AI Clipper Tool",
            access_token=acc["access_token"],
            refresh_token=acc.get("refresh_token", ""),
        )

    # Update clip record
    published = list(clip.get("published_to") or [])
    if "youtube_shorts" not in published:
        published.append("youtube_shorts")

    db.table("clips").update({
        "published_to": published,
        "youtube_short_url": result["url"],
    }).eq("id", clip_id).execute()

    return {"success": True, "youtube_url": result["url"]}
