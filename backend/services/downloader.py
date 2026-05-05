import yt_dlp
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

MAX_DURATION_SECONDS = 3 * 60 * 60  # 3 hours max


def get_video_info(youtube_url: str) -> dict:
    """Get metadata only — no download."""
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
    duration = info.get("duration", 0)
    if duration > MAX_DURATION_SECONDS:
        raise ValueError(f"Video too long ({duration // 60} min). Max is 60 minutes.")
    return {
        "video_id": info["id"],
        "title": info.get("title", "Unknown"),
        "duration": duration,
        "thumbnail": info.get("thumbnail", ""),
        "url": youtube_url,
    }


def download_audio_only(youtube_url: str, output_dir: str) -> str:
    """
    Download ONLY the audio track (~10-30 MB).
    Used for Whisper transcription — much faster than full video download.
    Returns path to the .m4a / .wav file.
    """
    out_template = f"{output_dir}/audio.%(ext)s"
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [],  # No conversion needed
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info(f"Downloading audio only: {youtube_url}")
        ydl.download([youtube_url])

    # Find the downloaded file
    for ext in ["m4a", "webm", "opus", "ogg", "mp3", "wav"]:
        path = f"{output_dir}/audio.{ext}"
        if os.path.exists(path):
            logger.info(f"Audio downloaded: {path} ({os.path.getsize(path) // 1024 // 1024}MB)")
            return path

    raise FileNotFoundError("Audio download failed — no file found")


def download_clip_segment(youtube_url: str, start: float, end: float, output_path: str) -> tuple[str, float]:
    """
    Download ONLY a specific time segment of the video using yt-dlp + FFmpeg.
    This avoids downloading the full video — just the clip portion.
    Returns (output_path, safe_start).
    """
    duration = end - start
    # Add 2s buffer on each side for safe cutting
    safe_start = max(0, start - 2)

    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "external_downloader": "ffmpeg",
        "external_downloader_args": {
            "ffmpeg_i": ["-ss", str(safe_start), "-t", str(duration + 4)]
        },
        "merge_output_format": "mp4",
        "postprocessors": [],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info(f"Downloading clip segment {start:.0f}s-{end:.0f}s")
        ydl.download([youtube_url])

    if not os.path.exists(output_path):
        # Sometimes yt-dlp adds extension — fix that
        for ext in ["mp4", "mkv", "webm"]:
            p = f"{output_path}.{ext}"
            if os.path.exists(p):
                os.rename(p, output_path)
                break

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Clip segment download failed: {output_path}")

    logger.info(f"Clip segment downloaded: {output_path}")
    return output_path, safe_start
