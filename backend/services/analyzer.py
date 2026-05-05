from groq import Groq
import json
import os
import logging

logger = logging.getLogger(__name__)
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def find_best_clips(transcript_segments, video_duration: int, num_clips: int = 3) -> list:
    """Use Llama 3.3 70B to identify the best viral moments."""
    formatted = ""
    for seg in transcript_segments:
        start = seg.start if hasattr(seg, "start") else seg.get("start", 0)
        end = seg.end if hasattr(seg, "end") else seg.get("end", 0)
        text = seg.text if hasattr(seg, "text") else seg.get("text", "")
        formatted += f"[{start:.1f}s - {end:.1f}s]: {text}\n"

    prompt = f"""You are a viral content expert for TikTok and YouTube Shorts.

Transcript with timestamps:
{formatted}

Video duration: {video_duration} seconds.

Find the {num_clips} best clips (30-90 seconds each). Look for:
- Strong hooks (grab attention in first 3 seconds)
- Surprising facts, insights, emotional peaks
- Funny or inspirational moments
- Self-contained stories that make sense without context

Rules:
- Each clip must be 30-90 seconds
- No overlapping ranges
- Return ONLY valid JSON, no other text

Format:
[
  {{"start": 45.2, "end": 89.0, "reason": "Why this is viral", "title": "Catchy short title"}},
  {{"start": 120.5, "end": 175.3, "reason": "Why this is viral", "title": "Catchy short title"}},
  {{"start": 240.0, "end": 295.0, "reason": "Why this is viral", "title": "Catchy short title"}}
]"""

    response = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()
    json_start = raw.find("[")
    json_end = raw.rfind("]") + 1
    if json_start == -1:
        raise ValueError(f"No JSON in Llama response: {raw[:300]}")

    clips = json.loads(raw[json_start:json_end])

    # Validate and filter
    valid = []
    for c in clips:
        dur = c.get("end", 0) - c.get("start", 0)
        if 15 <= dur <= 120 and c.get("start", 0) >= 0:
            valid.append(c)

    logger.info(f"Found {len(valid)} valid clips")
    return valid
