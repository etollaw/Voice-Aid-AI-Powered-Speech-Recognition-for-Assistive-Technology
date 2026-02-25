.PHONY: setup setup-backend setup-frontend backend frontend dev test lint format clean

# ── Setup ────────────────────────────────────────────────────
setup: setup-backend setup-frontend

setup-backend:
	cd backend && python -m venv venv && venv\Scripts\pip install -r requirements.txt

setup-frontend:
	cd frontend && npm install

# ── Run ──────────────────────────────────────────────────────
backend:
	cd backend && venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

# Run both (open two terminals, or use this with & on Unix)
dev:
	@echo "Run 'make backend' in one terminal and 'make frontend' in another."

# ── Test ─────────────────────────────────────────────────────
test:
	cd backend && venv\Scripts\pytest tests/ -v

test-cov:
	cd backend && venv\Scripts\pytest tests/ -v --cov=app --cov-report=html

# ── Lint & Format ────────────────────────────────────────────
lint:
	cd backend && venv\Scripts\ruff check app/ tests/
	cd frontend && npm run lint

format:
	cd backend && venv\Scripts\ruff format app/ tests/
	cd frontend && npm run format

# ── Clean ────────────────────────────────────────────────────
clean:
	rmdir /s /q backend\venv 2>nul || true
	rmdir /s /q backend\uploads 2>nul || true
	rmdir /s /q frontend\node_modules 2>nul || true
	rmdir /s /q frontend\dist 2>nul || true
	del /q backend\*.db 2>nul || true
