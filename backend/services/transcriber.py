from groq import Groq
import os
import subprocess
import logging

logger = logging.getLogger(__name__)
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def extract_audio(video_filepath: str, output_dir: str) -> str:
    """Extract mono 16kHz audio from video — keeps file under 25MB."""
    audio_path = f"{output_dir}/audio.mp3"
    result = subprocess.run([
        "ffmpeg", "-y", "-i", video_filepath,
        "-vn", "-ar", "16000", "-ac", "1", "-b:a", "32k",
        audio_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Audio extraction failed: {result.stderr}")

    file_size_mb = os.path.getsize(audio_path) / 1024 / 1024
    logger.info(f"Audio extracted: {file_size_mb:.1f} MB")

    if file_size_mb > 24:
        raise ValueError("Audio exceeds 24MB. Video is too long for Groq Whisper free tier.")

    return audio_path

def transcribe_audio(audio_filepath: str):
    """Transcribe with Groq Whisper, returns object with .segments and .text."""
    with open(audio_filepath, "rb") as f:
        transcription = _get_client().audio.transcriptions.create(
            file=f,
            model="whisper-large-v3",
            response_format="verbose_json",
            timestamp_granularities=["segment", "word"],
        )
    logger.info(f"Transcribed: {len(transcription.segments)} segments")
    return transcription
