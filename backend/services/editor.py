import subprocess
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_video_dimensions(video_path: str) -> dict:
    """Get width and height via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            return {"width": stream["width"], "height": stream["height"]}
    return {"width": 1920, "height": 1080}


def detect_face_center_x(video_path: str, orig_width: int) -> Optional[int]:
    """Sample a few frames and return average face center X, or None."""
    # Disabled mediapipe temporarily to prevent AVX Illegal Instruction crashes on MacOS.
    # Returns None so the editor gracefully falls back to a center-crop.
    return None


def generate_srt(segments, clip_start: float, clip_end: float) -> str:
    """Build SRT file content for a clip's segments."""
    def fmt(t: float) -> str:
        t = max(0.0, t)
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        ms = int((s % 1) * 1000)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"

    srt, n = "", 1
    for seg in segments:
        s = seg.start if hasattr(seg, "start") else seg.get("start", 0)
        e = seg.end if hasattr(seg, "end") else seg.get("end", 0)
        t = seg.text if hasattr(seg, "text") else seg.get("text", "")
        if e < clip_start or s > clip_end:
            continue
        rs, re = max(0, s - clip_start), max(0.1, e - clip_start)
        srt += f"{n}\n{fmt(rs)} --> {fmt(re)}\n{t.strip()}\n\n"
        n += 1
    return srt


def process_clip(input_path: str, start: float, end: float,
                 output_path: str, srt_path: str,
                 segment_is_precut: bool = False,
                 safe_start: float = 0.0) -> str:
    """
    Convert → face-crop → scale to 9:16 → burn subtitles → export.
    If segment_is_precut=True, the input is already cut to approx the clip,
    so we use a small offset instead of the full original timestamp.
    """
    temp = output_path.replace(".mp4", "_temp.mp4")

    try:
        if segment_is_precut:
            local_start = max(0, start - safe_start)
            local_end = local_start + (end - start)
        else:
            local_start = start
            local_end = end

        # 1. Fast cut using local timestamps
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(local_start), "-to", str(local_end),
            "-i", input_path, "-c", "copy", temp
        ], check=True, capture_output=True)

        if not os.path.exists(temp) or os.path.getsize(temp) < 1024:
            # Fallback: use the whole file
            import shutil
            shutil.copy(input_path, temp)

        # 2. Dimensions + face
        dims = get_video_dimensions(temp)
        w, h = dims["width"], dims["height"]
        target_w = int(h * 9 / 16)
        if target_w % 2:
            target_w -= 1

        face_x = detect_face_center_x(temp, w)
        if face_x is not None:
            crop_x = max(0, min(face_x - target_w // 2, w - target_w))
        else:
            crop_x = (w - target_w) // 2
        if crop_x % 2:
            crop_x -= 1

        # Build filter: crop → scale
        # (Subtitles are temporarily disabled because the local FFmpeg lacks libass support)
        vf = f"crop={target_w}:{h}:{crop_x}:0,scale=1080:1920"

        subprocess.run([
            "ffmpeg", "-y", "-i", temp,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            output_path
        ], check=True, capture_output=True)

        return output_path
    finally:
        if os.path.exists(temp):
            os.remove(temp)

