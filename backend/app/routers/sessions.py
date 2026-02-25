"""Session API endpoints: upload, list, get, delete, re-summarize."""

import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.database import get_db
from app.models import Session
from app.schemas import (
    ResummarizeRequest,
    SessionListItem,
    SessionListResponse,
    SessionResponse,
)
from app.services.audio import get_audio_duration, validate_audio_file
from app.services.summarization import summarize_transcript
from app.services.transcription import transcribe_audio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    """
    Upload an audio file, transcribe it, and generate a summary.

    This endpoint handles the full pipeline:
    1. Validate and save the uploaded audio file
    2. Transcribe using Whisper (or mock mode)
    3. Summarize the transcript
    4. Store everything in the database

    Returns the complete session with transcript and summary.
    """
    # Validate file type
    if not file.filename or not validate_audio_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Supported: mp3, wav, ogg, webm, m4a, flac, mp4",
        )

    # Check file size (read content to check)
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f}MB). Max allowed: {settings.max_file_size_mb}MB.",
        )

    # Create session record
    session_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix
    audio_filename = f"{session_id}{ext}"
    audio_path = str(settings.upload_dir / audio_filename)

    session = Session(
        id=session_id,
        audio_filename=audio_filename,
        status="uploading",
    )
    db.add(session)
    db.commit()

    try:
        # Save file
        with open(audio_path, "wb") as f:
            f.write(contents)

        # Get duration
        session.audio_duration = get_audio_duration(audio_path)

        # ── Transcribe ───────────────────────────────────
        session.status = "transcribing"
        db.commit()

        result = transcribe_audio(audio_path)
        session.transcript = result["text"]
        session.language = result.get("language", "en")
        session.word_count = len(result["text"].split()) if result["text"] else 0

        # ── Summarize ────────────────────────────────────
        session.status = "summarizing"
        db.commit()

        summary_result = summarize_transcript(result["text"])
        session.summary = summary_result["summary"]
        session.set_key_points(summary_result["key_points"])
        session.set_action_items(summary_result["action_items"])

        # Auto-generate title from first sentence of transcript
        if result["text"]:
            first_words = " ".join(result["text"].split()[:8])
            session.title = first_words + ("..." if len(result["text"].split()) > 8 else "")
        else:
            session.title = f"Session {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"

        session.status = "completed"
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)

    except Exception as e:
        logger.error(f"Processing failed for session {session_id}: {e}")
        session.status = "error"
        session.error_message = str(e)
        db.commit()
        db.refresh(session)

    return _session_to_response(session)


@router.get("", response_model=SessionListResponse)
def list_sessions(
    search: str | None = Query(None, description="Search in title/transcript"),
    status: str | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DBSession = Depends(get_db),
):
    """List all sessions with optional search and pagination."""
    query = db.query(Session)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Session.title.ilike(search_filter)) | (Session.transcript.ilike(search_filter))
        )

    if status:
        query = query.filter(Session.status == status)

    total = query.count()
    sessions = (
        query.order_by(Session.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return SessionListResponse(
        sessions=[
            SessionListItem(
                id=s.id,
                title=s.title,
                audio_duration=s.audio_duration,
                status=s.status,
                language=s.language,
                word_count=s.word_count,
                created_at=s.created_at,
            )
            for s in sessions
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    """Get a single session by ID."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_response(session)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: str, db: DBSession = Depends(get_db)):
    """Delete a session and its audio file."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete audio file
    if session.audio_filename:
        audio_path = settings.upload_dir / session.audio_filename
        if audio_path.exists():
            audio_path.unlink()

    db.delete(session)
    db.commit()


@router.post("/{session_id}/resummarize", response_model=SessionResponse)
def resummarize_session(
    session_id: str,
    body: ResummarizeRequest,
    db: DBSession = Depends(get_db),
):
    """Re-run summarization on an existing session with different settings."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.transcript:
        raise HTTPException(status_code=400, detail="No transcript available to summarize")

    try:
        result = summarize_transcript(session.transcript, num_sentences=body.sentence_count)
        session.summary = result["summary"]
        session.set_key_points(result["key_points"])
        session.set_action_items(result["action_items"])
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")

    return _session_to_response(session)


def _session_to_response(session: Session) -> SessionResponse:
    """Convert ORM Session to Pydantic response."""
    return SessionResponse(
        id=session.id,
        title=session.title,
        audio_filename=session.audio_filename,
        audio_duration=session.audio_duration,
        status=session.status,
        error_message=session.error_message,
        transcript=session.transcript,
        summary=session.summary,
        key_points=session.get_key_points(),
        action_items=session.get_action_items(),
        language=session.language,
        word_count=session.word_count,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )
