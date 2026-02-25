"""Application configuration via environment variables."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from environment / .env file."""

    # General
    app_name: str = "VoiceAid"
    debug: bool = True
    mock_mode: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    upload_dir: Path = Path(__file__).resolve().parent.parent / "uploads"
    db_path: Path = Path(__file__).resolve().parent.parent / "voiceaid.db"

    # Database
    database_url: str = ""

    # Whisper
    whisper_model: str = "base"  # tiny, base, small, medium, large
    whisper_language: str | None = None  # None = auto-detect

    # Summarization
    summary_sentence_count: int = 5
    summary_model: str = "extractive"  # extractive (rule-based) or transformers

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Limits
    max_file_size_mb: int = 100
    max_audio_duration_sec: int = 3600  # 1 hour

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.database_url:
            self.database_url = f"sqlite:///{self.db_path}"
        self.upload_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
