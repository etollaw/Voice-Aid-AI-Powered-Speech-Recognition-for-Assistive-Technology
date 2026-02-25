"""Transcription service using AssemblyAI with mock fallback.

AssemblyAI free tier: 100 hours/month of transcription.
Sign up at https://www.assemblyai.com/ to get an API key.
"""

import logging
import time

import requests

from app.config import settings

logger = logging.getLogger(__name__)

ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLYAI_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"


def _mock_transcribe(audio_path: str) -> dict:
    """Return a mock transcript for development/testing."""
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


def _upload_to_assemblyai(audio_path: str) -> str:
    """Upload a local audio file to AssemblyAI and return the upload URL."""
    headers = {"authorization": settings.assemblyai_api_key}

    with open(audio_path, "rb") as f:
        response = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=headers, data=f)

    if response.status_code != 200:
        raise RuntimeError(f"AssemblyAI upload failed ({response.status_code}): {response.text}")

    return response.json()["upload_url"]


def _request_transcription(audio_url: str, language: str | None = None) -> str:
    """Request transcription and return the transcript ID."""
    headers = {
        "authorization": settings.assemblyai_api_key,
        "content-type": "application/json",
    }
    payload: dict = {"audio_url": audio_url}

    if language:
        payload["language_code"] = language
    else:
        payload["language_detection"] = True

    response = requests.post(ASSEMBLYAI_TRANSCRIPT_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"AssemblyAI transcription request failed ({response.status_code}): {response.text}"
        )

    return response.json()["id"]


def _poll_transcript(transcript_id: str, timeout_sec: int = 300) -> dict:
    """Poll AssemblyAI until the transcript is ready."""
    headers = {"authorization": settings.assemblyai_api_key}
    url = f"{ASSEMBLYAI_TRANSCRIPT_URL}/{transcript_id}"

    start = time.time()
    while time.time() - start < timeout_sec:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data["status"] == "completed":
            return data
        elif data["status"] == "error":
            raise RuntimeError(f"AssemblyAI transcription error: {data.get('error', 'unknown')}")

        logger.info(f"Transcription status: {data['status']}... waiting 3s")
        time.sleep(3)

    raise RuntimeError(f"Transcription timed out after {timeout_sec}s")


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe an audio file to text using AssemblyAI.

    In mock mode, returns a fixed demo transcript (no API call).

    Args:
        audio_path: Path to the audio file.

    Returns:
        dict with keys: 'text' (str), 'language' (str)
    """
    if settings.mock_mode:
        logger.info("Using mock transcription (MOCK_MODE=true)")
        return _mock_transcribe(audio_path)

    if not settings.assemblyai_api_key:
        raise RuntimeError(
            "ASSEMBLYAI_API_KEY is not set. "
            "Get a free key at https://www.assemblyai.com/ and add it to your .env file."
        )

    logger.info(f"Uploading audio to AssemblyAI: {audio_path}")
    audio_url = _upload_to_assemblyai(audio_path)

    logger.info("Requesting transcription...")
    transcript_id = _request_transcription(audio_url, settings.whisper_language)

    logger.info(f"Polling for transcript {transcript_id}...")
    result = _poll_transcript(transcript_id)

    detected_language = result.get("language_code", "en")
    text = result.get("text", "") or ""

    logger.info(f"Transcription complete: {len(text)} chars, language={detected_language}")

    return {
        "text": text,
        "language": detected_language,
    }
