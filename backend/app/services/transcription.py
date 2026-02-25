"""Transcription service using OpenAI Whisper with mock fallback."""

import logging
import time

from app.config import settings
from app.services.audio import chunk_audio, cleanup_chunks

logger = logging.getLogger(__name__)

# Lazy-loaded Whisper model (loaded on first use)
_whisper_model = None


def _load_whisper_model():
    """Load Whisper model (lazy, cached)."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model

    try:
        import whisper

        logger.info(f"Loading Whisper model '{settings.whisper_model}'...")
        start = time.time()
        _whisper_model = whisper.load_model(settings.whisper_model)
        logger.info(f"Whisper model loaded in {time.time() - start:.1f}s")
        return _whisper_model
    except ImportError:
        logger.error("openai-whisper is not installed. Install it or enable MOCK_MODE.")
        raise RuntimeError(
            "Whisper is not installed. Run 'pip install openai-whisper' or set MOCK_MODE=true."
        )
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise RuntimeError(f"Failed to load Whisper model: {e}")


def _mock_transcribe(audio_path: str) -> dict:
    """Return a mock transcript for development/testing without Whisper."""
    return {
        "text": (
            "Welcome to the VoiceAid demo session. "
            "Today we need to discuss the project timeline and assign tasks. "
            "First, we should finalize the design mockups by Friday. "
            "Sarah will handle the frontend implementation. "
            "We need to set up the CI/CD pipeline before next week. "
            "Action item: John should review the API documentation. "
            "Action item: Schedule a follow-up meeting for Monday. "
            "The budget needs to be approved by the finance team. "
            "Let's make sure we have unit tests for all critical paths. "
            "Thanks everyone for joining today's meeting."
        ),
        "language": "en",
    }


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe an audio file to text.

    Handles long audio via chunking (splits at 5-min intervals).
    Falls back to mock mode if MOCK_MODE is enabled.

    Args:
        audio_path: Path to the audio file.

    Returns:
        dict with keys: 'text' (str), 'language' (str)
    """
    if settings.mock_mode:
        logger.info("Using mock transcription (MOCK_MODE=true)")
        return _mock_transcribe(audio_path)

    model = _load_whisper_model()

    # Chunk long audio files
    chunk_paths = chunk_audio(audio_path, chunk_duration_sec=300)

    transcripts = []
    detected_language = None

    try:
        for i, chunk_path in enumerate(chunk_paths):
            logger.info(f"Transcribing chunk {i+1}/{len(chunk_paths)}: {chunk_path}")

            options = {}
            if settings.whisper_language:
                options["language"] = settings.whisper_language

            result = model.transcribe(chunk_path, **options)

            transcripts.append(result["text"].strip())
            if detected_language is None:
                detected_language = result.get("language", "en")

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        # If partial results exist, return them
        if transcripts:
            logger.warning("Returning partial transcript due to error.")
        else:
            raise RuntimeError(f"Transcription failed: {e}")
    finally:
        cleanup_chunks(chunk_paths, audio_path)

    full_text = " ".join(transcripts)

    return {
        "text": full_text,
        "language": detected_language or "en",
    }
