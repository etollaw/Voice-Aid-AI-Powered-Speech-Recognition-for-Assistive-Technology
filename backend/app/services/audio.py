"""Audio processing utilities: duration, format conversion, chunking.

Uses subprocess + ffprobe/ffmpeg for audio operations to avoid
pydub's audioop dependency issue on Python 3.13.
"""

import json
import logging
import math
import shutil
import subprocess
import wave
from pathlib import Path

logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".ogg", ".webm", ".m4a", ".flac", ".mp4", ".mpeg", ".wma"}

# Check if ffmpeg/ffprobe are available
_FFMPEG = shutil.which("ffmpeg")
_FFPROBE = shutil.which("ffprobe")


def validate_audio_file(filename: str) -> bool:
    """Check if the file extension is a supported audio format."""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_FORMATS


def get_audio_duration(file_path: str) -> float:
    """Get audio duration in seconds."""
    # Try ffprobe first (works for any format)
    if _FFPROBE:
        try:
            result = subprocess.run(
                [
                    _FFPROBE, "-v", "quiet", "-print_format", "json",
                    "-show_format", file_path,
                ],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return float(info["format"]["duration"])
        except Exception as e:
            logger.debug(f"ffprobe duration failed: {e}")

    # Fallback for WAV files
    try:
        with wave.open(file_path, "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception as e:
        logger.warning(f"Could not determine audio duration: {e}")
        return 0.0


def convert_to_wav(input_path: str, output_path: str | None = None) -> str:
    """Convert any supported audio format to WAV (16kHz mono) for Whisper."""
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".wav"))

    if not _FFMPEG:
        logger.warning("ffmpeg not found; returning original file")
        return input_path

    try:
        subprocess.run(
            [
                _FFMPEG, "-y", "-i", input_path,
                "-ar", "16000", "-ac", "1", "-f", "wav", output_path,
            ],
            capture_output=True, timeout=120, check=True,
        )
        return output_path
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise ValueError(f"Could not convert audio file: {e}")


def chunk_audio(file_path: str, chunk_duration_sec: int = 300) -> list[str]:
    """
    Split a long audio file into chunks for processing.

    Uses ffmpeg for chunking. If ffmpeg is unavailable, returns the original
    file as a single chunk (Whisper can handle it, just slower).

    Args:
        file_path: Path to the audio file.
        chunk_duration_sec: Max duration per chunk in seconds (default 5 min).

    Returns:
        List of paths to chunk files. If audio is shorter than chunk_duration,
        returns a list with just the original file.
    """
    duration = get_audio_duration(file_path)
    if duration <= 0 or duration <= chunk_duration_sec:
        return [file_path]

    if not _FFMPEG:
        logger.warning("ffmpeg not found; skipping chunking")
        return [file_path]

    num_chunks = math.ceil(duration / chunk_duration_sec)
    chunk_paths = []
    base = Path(file_path)

    for i in range(num_chunks):
        start = i * chunk_duration_sec
        chunk_path = str(base.parent / f"{base.stem}_chunk{i}.wav")
        try:
            subprocess.run(
                [
                    _FFMPEG, "-y", "-i", file_path,
                    "-ss", str(start), "-t", str(chunk_duration_sec),
                    "-ar", "16000", "-ac", "1", "-f", "wav", chunk_path,
                ],
                capture_output=True, timeout=120, check=True,
            )
            chunk_paths.append(chunk_path)
            logger.info(f"Created chunk {i+1}/{num_chunks}: {chunk_path}")
        except Exception as e:
            logger.error(f"Chunking failed at segment {i}: {e}")
            # If partial chunks exist, use them; otherwise fall back to original
            if not chunk_paths:
                return [file_path]
            break

    return chunk_paths


def cleanup_chunks(chunk_paths: list[str], original_path: str):
    """Remove temporary chunk files (but not the original)."""
    for path in chunk_paths:
        if path != original_path:
            try:
                Path(path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Could not clean up chunk {path}: {e}")
