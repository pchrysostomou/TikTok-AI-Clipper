from fastapi import APIRouter, HTTPException
from models import ProcessRequest, ProcessResponse
from database import get_db
import os, sys, subprocess, logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Absolute path to the worker script (lives in backend/, not backend/routes/)
WORKER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "pipeline_worker.py")


@router.post("/process", response_model=ProcessResponse)
async def process_video(req: ProcessRequest):
    if "youtube.com" not in req.youtube_url and "youtu.be" not in req.youtube_url:
        raise HTTPException(400, "Invalid YouTube URL")

    try:
        db = get_db()
        job = db.table("processing_jobs").insert({
            "user_id": req.user_id,
            "youtube_url": req.youtube_url,
            "status": "pending",
        }).execute()
        job_id = job.data[0]["id"]
    except Exception as e:
        logger.error(f"Database error during process initiation: {e}")
        raise HTTPException(500, f"Failed to connect to database. Is Supabase configured correctly? ({e})")

    # Launch a completely separate subprocess — 100% non-blocking
    subprocess.Popen(
        [sys.executable, WORKER_SCRIPT, job_id, req.youtube_url, req.user_id],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,   # Detach from this process group
    )
    logger.info(f"[{job_id}] Worker subprocess launched for {req.youtube_url}")

    return ProcessResponse(
        status="processing",
        job_id=job_id,
        message="Pipeline started. Audio-first approach — ~3-5 min total.",
    )
