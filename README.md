# VoiceAid — AI-Powered Speech Recognition for Assistive Technology

An AI-driven voice-to-notes platform that transcribes audio, generates summaries, extracts key points and action items. Designed for accessibility, runs fully locally.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Record or upload** audio files (MP3, WAV, OGG, WebM, M4A, FLAC)
- **AI transcription** via OpenAI Whisper (runs locally, no API keys)
- **Smart summaries** with extractive summarization (fast, deterministic)
- **Key points** auto-extracted from transcript
- **Action items** detected via NLP pattern matching
- **Session history** with search and pagination
- **Accessible, clean UI** built with React + Tailwind CSS
- **Mock mode** for development without ML models

---

## Architecture

```
┌─────────────────────┐        HTTP/JSON        ┌────────────────────────┐
│  Frontend (React)    │ ◄─────────────────────► │  Backend (FastAPI)      │
│  Vite + Tailwind     │    localhost:5173        │  uvicorn :8000          │
│  React Router        │    (proxy to 8000)       │                        │
└─────────────────────┘                          │  ├─ Whisper (ASR)       │
                                                 │  ├─ Extractive summary  │
                                                 │  └─ SQLite database     │
                                                 └────────────────────────┘
```

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **FFmpeg** (required by Whisper for audio processing)
  - Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### 1. Clone & Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
copy .env.example .env   # Windows
# cp .env.example .env   # Mac/Linux
```

### 2. Setup Frontend

```bash
cd frontend
npm install
```

### 3. Run (Development)

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate        # or: source venv/bin/activate
set MOCK_MODE=true           # Windows (skip Whisper download for quick testing)
# export MOCK_MODE=true      # Mac/Linux
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Run with Real Transcription

```bash
cd backend
venv\Scripts\activate
set MOCK_MODE=false
set WHISPER_MODEL=base       # Options: tiny, base, small, medium, large
uvicorn app.main:app --reload
```

> First run will download the Whisper model (~140MB for `base`). The `tiny` model (~75MB) is fastest for testing.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check + config info |
| `POST` | `/api/sessions` | Upload audio → transcribe → summarize |
| `GET` | `/api/sessions` | List sessions (supports `?search=`, `?page=`, `?status=`) |
| `GET` | `/api/sessions/{id}` | Get single session detail |
| `DELETE` | `/api/sessions/{id}` | Delete a session |
| `POST` | `/api/sessions/{id}/resummarize` | Re-summarize with different settings |

Full OpenAPI docs at **http://localhost:8000/docs** when backend is running.

### Example: Upload Audio

```bash
curl -X POST http://localhost:8000/api/sessions \
  -F "file=@meeting.wav"
```

Response:
```json
{
  "id": "abc-123",
  "title": "Welcome to the VoiceAid demo...",
  "status": "completed",
  "transcript": "Welcome to the VoiceAid demo session...",
  "summary": "The team discussed project timelines...",
  "key_points": ["Finalize design mockups by Friday"],
  "action_items": ["John should review the API documentation"],
  "word_count": 98,
  "language": "en",
  "audio_duration": 45.2
}
```

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings (env vars)
│   │   ├── database.py          # SQLAlchemy + SQLite
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   └── sessions.py      # API endpoints
│   │   └── services/
│   │       ├── audio.py         # Audio utils (duration, chunking)
│   │       ├── transcription.py # Whisper integration
│   │       └── summarization.py # Extractive summarization
│   ├── tests/
│   │   ├── test_api.py          # API endpoint tests
│   │   └── test_services.py     # Unit tests for services
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Router setup
│   │   ├── api/client.js        # API client
│   │   ├── hooks/useRecorder.js # Audio recording hook
│   │   ├── components/          # Reusable UI components
│   │   └── pages/               # Page components
│   ├── package.json
│   └── vite.config.js
├── Makefile
└── README.md
```

---

## Running Tests

```bash
cd backend
venv\Scripts\activate
pytest tests/ -v
```

Tests run in mock mode automatically (no Whisper needed).

---

## Linting & Formatting

```bash
# Backend
cd backend
ruff check app/ tests/        # Lint
ruff format app/ tests/       # Format

# Frontend
cd frontend
npm run lint                  # ESLint
npm run format                # Prettier
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_MODE` | `false` | Skip Whisper, use dummy transcripts |
| `WHISPER_MODEL` | `base` | Whisper model: tiny/base/small/medium/large |
| `WHISPER_LANGUAGE` | (auto) | Force language code (e.g., `en`) |
| `SUMMARY_SENTENCE_COUNT` | `5` | Sentences in summary |
| `MAX_FILE_SIZE_MB` | `100` | Max upload file size |
| `DEBUG` | `true` | Enable debug logging |

### Whisper Model Sizes

| Model | Size | RAM | Speed | Accuracy |
|-------|------|-----|-------|----------|
| tiny | 75MB | ~1GB | Fastest | Good |
| base | 140MB | ~1GB | Fast | Better |
| small | 460MB | ~2GB | Medium | Great |
| medium | 1.5GB | ~5GB | Slow | Excellent |
| large | 3GB | ~10GB | Slowest | Best |

---

## Deployment

### Frontend (Vercel)

1. Push to GitHub
2. Import in Vercel → set **Root directory**: `frontend`
3. Build command: `npm run build` → Output: `dist`
4. Env var: `VITE_API_URL` = your backend URL

### Backend (Railway / Render)

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## License

MIT
