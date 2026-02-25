"""SQLAlchemy ORM models."""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


def _generate_uuid():
    return str(uuid.uuid4())


def _utcnow():
    return datetime.now(timezone.utc)


class Session(Base):
    """A voice recording session with transcript and summary."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    title = Column(String(255), nullable=False, default="Untitled Session")
    audio_filename = Column(String(255), nullable=True)
    audio_duration = Column(Float, nullable=True)  # seconds
    status = Column(
        String(20), nullable=False, default="uploading"
    )  # uploading | transcribing | summarizing | completed | error
    error_message = Column(Text, nullable=True)

    # Content
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)  # JSON list
    action_items = Column(Text, nullable=True)  # JSON list

    # Metadata
    language = Column(String(10), nullable=True)
    word_count = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def get_key_points(self) -> list[str]:
        if self.key_points:
            return json.loads(self.key_points)
        return []

    def set_key_points(self, points: list[str]):
        self.key_points = json.dumps(points)

    def get_action_items(self) -> list[str]:
        if self.action_items:
            return json.loads(self.action_items)
        return []

    def set_action_items(self, items: list[str]):
        self.action_items = json.dumps(items)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "audio_filename": self.audio_filename,
            "audio_duration": self.audio_duration,
            "status": self.status,
            "error_message": self.error_message,
            "transcript": self.transcript,
            "summary": self.summary,
            "key_points": self.get_key_points(),
            "action_items": self.get_action_items(),
            "language": self.language,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
