# AI Quiz Generator

Generate multiple-choice quizzes from a topic or uploaded document using OpenAI-compatible models.

## Repository Structure

```
backend/    # FastAPI backend (Python 3.11+)
frontend/   # React frontend (Vite + TypeScript) — added in Phase 3
```

## Frontend — Local Development

```bash
cd frontend
npm install
npm run dev          # API via Vite proxy → http://127.0.0.1:8080 (start backend locally first)
npm run dev:remote   # API → Railway dev host from `frontend/.env.remote` (CORS must allow http://localhost:5173)
```

## Backend — Local Development

### Prerequisites

- Python 3.11+

### Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set OPENAI_API_KEY to your openai-hk.com key
uvicorn app.main:app --reload --port 8080
```

The server starts at `http://localhost:8080` (typical Railway `PORT`; the public Railway URL still uses HTTPS without `:8080`).

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | — | API key for the LLM proxy |
| `OPENAI_BASE_URL` | No | `https://api.openai-hk.com/v1` | LLM proxy base URL |
| `ALLOWED_ORIGINS` | No | `*` | CORS origins — `*` or comma-separated list |
| `AVAILABLE_MODELS` | No | three-model fallback (includes `gpt-4.1`) | JSON array of `{"id","label"}`; confirm each `id` with your provider |
| `ENABLE_DEBUG_CHAT_COMPLETION` | No | `false` | Enables debug LLM smoke route |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check — returns `{"status":"ok","timestamp":"..."}` |
| `GET` | `/api/models` | Available model list from `AVAILABLE_MODELS` env var |
| `POST` | `/api/debug/chat-completion` | **Gated** LLM smoke test (see below) |

### Debug Route

`POST /api/debug/chat-completion` verifies LLM connectivity during development.

> ⚠️ **Production warning:** Set `ENABLE_DEBUG_CHAT_COMPLETION=false` (or leave unset) on any
> public production deployment. When the flag is false, this route does not exist.

Request body:

```json
{
  "model": "gpt-4o-mini",
  "message": "optional custom prompt (defaults to a short test phrase)"
}
```

Response:

```json
{
  "reply": "...",
  "model_used": "gpt-4o-mini"
}
```

`model` must be in the `AVAILABLE_MODELS` allowlist — requests with unlisted models return HTTP 400.
Server hard-caps `max_tokens` at 64 regardless of request content.

## Deployment

Backend is deployed to [Railway](https://railway.app):

1. Create a new Railway project from this GitHub repository.
2. Set **Root Directory** to `backend/` in Railway project settings.
3. Add all environment variables from the table above in the Railway **Variables** tab.
4. Railway auto-detects `Procfile` and `requirements.txt` — no additional config needed.
