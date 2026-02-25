"""Pytest fixtures for backend tests."""

import os
import struct
import wave

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force mock mode for tests
os.environ["MOCK_MODE"] = "true"


@pytest.fixture(scope="function")
def client(tmp_path):
    """FastAPI test client with a fresh test database per test."""
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Patch the database module BEFORE importing the app
    import app.database as db_mod
    original_engine = db_mod.engine
    original_session_local = db_mod.SessionLocal

    db_mod.engine = engine
    db_mod.SessionLocal = TestingSession

    from app.database import Base, get_db
    from app.main import app

    # Create tables
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    db_mod.engine = original_engine
    db_mod.SessionLocal = original_session_local


@pytest.fixture
def sample_wav(tmp_path):
    """Create a minimal valid WAV file for testing."""
    wav_path = tmp_path / "test.wav"
    with wave.open(str(wav_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        # 1 second of silence
        frames = struct.pack("<" + "h" * 16000, *([0] * 16000))
        wf.writeframes(frames)
    return str(wav_path)
