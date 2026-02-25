"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import sessions
from app.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info(f"Starting {settings.app_name} API")
    logger.info(f"Mock mode: {settings.mock_mode}")
    logger.info(f"Whisper model: {settings.whisper_model}")
    init_db()
    logger.info("Database initialized.")
    yield  # ← app is running
    logger.info("Shutting down.")


# Create app
app = FastAPI(
    title="VoiceAid API",
    description="Voice-powered accessibility tool: transcribe audio, generate summaries and action items.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ───────────────────────────────────────────────────
app.include_router(sessions.router)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        mock_mode=settings.mock_mode,
        whisper_model=settings.whisper_model,
    )
