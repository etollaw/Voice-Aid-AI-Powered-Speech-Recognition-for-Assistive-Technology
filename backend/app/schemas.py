"""Pydantic schemas for API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


# ── Response schemas ─────────────────────────────────────────


class SessionResponse(BaseModel):
    id: str
    title: str
    audio_filename: str | None = None
    audio_duration: float | None = None
    status: str
    error_message: str | None = None
    transcript: str | None = None
    summary: str | None = None
    key_points: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    language: str | None = None
    word_count: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SessionListItem(BaseModel):
    id: str
    title: str
    audio_duration: float | None = None
    status: str
    language: str | None = None
    word_count: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionListItem]
    total: int
    page: int
    page_size: int


class ResummarizeRequest(BaseModel):
    sentence_count: int = Field(default=5, ge=1, le=20)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    mock_mode: bool = False
    whisper_model: str = "base"


class ErrorResponse(BaseModel):
    detail: str
