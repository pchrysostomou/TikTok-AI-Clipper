"""
Pipeline worker — runs as a separate subprocess.
Called by: python3 pipeline_worker.py <job_id> <youtube_url> <user_id>
"""
import sys
import os

# Load env first
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import tempfile, uuid, logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pipeline_worker")


def main():
    if len(sys.argv) < 4:
        print("Usage: pipeline_worker.py <job_id> <youtube_url> <user_id>")
        sys.exit(1)

    job_id = sys.argv[1]
    youtube_url = sys.argv[2]
    user_id = sys.argv[3]

    logger.info(f"[{job_id}] Worker started PID={os.getpid()}")

    from database import get_db
    import cloudinary
    import cloudinary.uploader
    from services import downloader, transcriber, analyzer, editor

    # Configure cloudinary
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    )

    def update_job(status: str, **kwargs):
        db = get_db()
        data = {"status": status, **kwargs}
        if status in ("done", "failed"):
            data["completed_at"] = datetime.now(timezone.utc).isoformat()
        db.table("processing_jobs").update(data).eq("id", job_id).execute()

    with tempfile.TemporaryDirectory() as tmp:
        try:
            # 1. Metadata
            logger.info(f"[{job_id}] Step 1: Getting video info")
            update_job("downloading")
            info = downloader.get_video_info(youtube_url)
            update_job("downloading",
                       youtube_title=info["title"],
                       youtube_thumbnail=info.get("thumbnail", ""))
            logger.info(f"[{job_id}] Video: '{info['title']}' ({info['duration']//60} min)")

            # 2. Audio-only download
            logger.info(f"[{job_id}] Step 2: Downloading audio only")
            audio_path = downloader.download_audio_only(youtube_url, tmp)

            # 3. Transcribe
            logger.info(f"[{job_id}] Step 3: Transcribing with Whisper")
            update_job("transcribing")
            whisper_audio = transcriber.extract_audio(audio_path, tmp)
            transcript = transcriber.transcribe_audio(whisper_audio)

            # 4. Analyze
            logger.info(f"[{job_id}] Step 4: Analyzing with Llama 3.3")
            update_job("analyzing")
            clips = analyzer.find_best_clips(transcript.segments, info["duration"])
            if not clips:
                raise ValueError("AI found no suitable viral clips")
            logger.info(f"[{job_id}] Found {len(clips)} clips")

            # 5. Edit + upload each clip
            update_job("editing")
            db = get_db()
            for i, clip in enumerate(clips):
                logger.info(f"[{job_id}] Clip {i+1}/{len(clips)}: {clip['start']:.0f}s-{clip['end']:.0f}s")

                segment_path = f"{tmp}/segment_{i}.mp4"
                _, safe_start = downloader.download_clip_segment(youtube_url, clip["start"], clip["end"], segment_path)

                srt = editor.generate_srt(transcript.segments, clip["start"], clip["end"])
                srt_path = f"{tmp}/clip_{i}.srt"
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt)

                out_path = f"{tmp}/clip_{i}_final.mp4"
                editor.process_clip(segment_path, clip["start"], clip["end"],
                                    out_path, srt_path, segment_is_precut=True, safe_start=safe_start)

                update_job("uploading")
                result = cloudinary.uploader.upload(
                    out_path, resource_type="video",
                    folder=f"clips/{user_id}",
                    public_id=f"clip_{uuid.uuid4().hex[:8]}",
                )

                db.table("clips").insert({
                    "job_id": job_id,
                    "user_id": user_id,
                    "title": clip.get("title", f"Clip {i+1}"),
                    "ai_reason": clip.get("reason", ""),
                    "start_time": clip["start"],
                    "end_time": clip["end"],
                    "duration": clip["end"] - clip["start"],
                    "cloudinary_url": result["secure_url"],
                    "cloudinary_public_id": result["public_id"],
                    "published_to": [],
                }).execute()
                logger.info(f"[{job_id}] ✅ Clip {i+1} uploaded: {result['secure_url']}")

            update_job("done")
            logger.info(f"[{job_id}] 🎉 Done — {len(clips)} clips ready!")

        except Exception as exc:
            logger.error(f"[{job_id}] ❌ Failed: {exc}", exc_info=True)
            update_job("failed", error_message=str(exc))


if __name__ == "__main__":
    main()
