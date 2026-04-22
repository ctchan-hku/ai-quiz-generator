---
phase: 01-backend-scaffold
goal: >
  A deployable FastAPI backend is publicly reachable on Railway with working
  health and model endpoints, plus an optional gated LLM smoke route for manual testing.
status: complete
requirements: BACK-01, BACK-02, BACK-03, BACK-07, DEPLOY-01, DEPLOY-03
decisions: D-01, D-02, D-03, D-04, D-05, D-06, D-07, D-08, D-09, D-10
---

# Phase 1: Backend Scaffold — PLAN

**Goal:** A deployable FastAPI backend is publicly reachable on Railway with working health and model endpoints, plus an optional gated LLM smoke route for manual testing.

**Status:** Complete — UAT passed (`01-UAT.md`); all six tests recorded pass
**Requirements:** BACK-01, BACK-02, BACK-03, BACK-07, DEPLOY-01, DEPLOY-03

---

## Wave Structure

| Wave | Plans | Parallelism |
|------|-------|-------------|
| 1 | **Plan 02** (Config), **Plan 04** (Railway Files + README) | Run in parallel — no shared files |
| 2 | **Plan 01** (App Scaffold + Routes) | Depends on Plan 02 (imports `app.config`) |
| 3 | **Plan 03** (Debug Route) | Depends on Plans 01 + 02 — modifies `main.py` |
| 4 | **Plan 05** (Deploy to Railway) | Depends on Plans 01–04 — human action |
| 5 | **Plan 06** (Smoke Test) | Depends on Plan 05 — human verify |

> Execute Wave 1 plans in parallel, then proceed wave by wave.

---

## Plan 02 — pydantic-settings Config Module

**Wave:** 1 | **Depends on:** nothing
**Objective:** Create the single source of truth for all environment variables, including parsed model list, CORS origins, and debug gate flag.
**Requirements:** BACK-01, BACK-03, DEPLOY-03
**Type:** execute | **Autonomous:** true

### Files
- `backend/app/config.py` ← new

---

### Task 2.1 — Implement `Settings` class

**File:** `backend/app/config.py`

**Action:** Create `backend/app/config.py` with this exact content:

```python
import json
import logging
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_FALLBACK_MODELS: list[dict[str, str]] = [
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini (fast)"},
    {"id": "gpt-4o", "label": "GPT-4o (smart)"},
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM proxy — required; startup fails with a clear error if absent
    openai_api_key: str
    openai_base_url: str = "https://api.openai-hk.com/v1"

    # CORS — Phase 1: ALLOWED_ORIGINS=* (D-06); Phase 3: tighten to Vercel + localhost (D-07)
    allowed_origins_raw: str = Field("*", validation_alias="ALLOWED_ORIGINS")

    # Model list as JSON array env var (D-03)
    available_models_raw: str = Field(
        json.dumps(_FALLBACK_MODELS),
        validation_alias="AVAILABLE_MODELS",
    )

    # Debug route gate — defaults to False; MUST remain False on production (D-08, D-10)
    enable_debug_chat_completion: bool = False

    @property
    def allowed_origins(self) -> list[str]:
        """Return list of allowed CORS origins from the ALLOWED_ORIGINS env var.

        Returns ["*"] when the raw value is the literal string "*".
        Splits on commas for multi-origin Phase 3 config (D-07).
        """
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @property
    def available_models(self) -> list[dict[str, Any]]:
        """Parse AVAILABLE_MODELS JSON array. Falls back to hardcoded list on parse error."""
        try:
            parsed = json.loads(self.available_models_raw)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("AVAILABLE_MODELS is not valid JSON; using fallback model list")
        return _FALLBACK_MODELS

    @property
    def available_model_ids(self) -> set[str]:
        """Set of allowlisted model ID strings for debug route validation (D-09)."""
        return {m["id"] for m in self.available_models}


settings = Settings()
```

**Field contract:**
- `openai_api_key`: reads `OPENAI_API_KEY`. No default — app fails to start if absent. Desired: Railway will surface the missing-variable error at deploy time.
- `openai_base_url`: reads `OPENAI_BASE_URL`. Defaults to `https://api.openai-hk.com/v1` per project specifics.
- `allowed_origins_raw`: `validation_alias="ALLOWED_ORIGINS"` tells pydantic-settings to read the `ALLOWED_ORIGINS` env var into this field (field name differs from env var name intentionally to avoid name collision with the property).
- `available_models_raw`: same pattern for `AVAILABLE_MODELS`.
- `enable_debug_chat_completion`: reads `ENABLE_DEBUG_CHAT_COMPLETION`; pydantic-settings coerces `"true"`/`"false"` strings to `bool` automatically.
- Module-level `settings = Settings()` — all routers import `from app.config import settings`.

**Verify:**
```bash
cd backend
OPENAI_API_KEY=test python3 -c "
from app.config import settings
assert settings.allowed_origins == ['*'], f'expected [\"*\"], got {settings.allowed_origins}'
assert len(settings.available_models) >= 2
assert 'gpt-4o-mini' in settings.available_model_ids
assert 'gpt-4o' in settings.available_model_ids
assert settings.enable_debug_chat_completion is False
print('config OK')
"
```

**Done:** `settings` instantiates; `allowed_origins == ["*"]`; `available_models` returns two-entry list; `enable_debug_chat_completion` is `False` by default.

---

### Verification (Plan 02 complete)

```bash
cd backend
OPENAI_API_KEY=sk-test python3 -c "
from app.config import settings
print('models:', settings.available_models)
print('origins:', settings.allowed_origins)
print('debug gate:', settings.enable_debug_chat_completion)
"
```

Output includes model list, `['*']` for origins, and `False` for debug gate.

---

## Plan 04 — Railway Config Files + README

**Wave:** 1 | **Depends on:** nothing (parallel with Plan 02)
**Objective:** Create all deployment configuration and documentation so Railway auto-detects and runs the app, and developers know how to set up locally.
**Requirements:** DEPLOY-01, DEPLOY-03, BACK-07 (README warning, D-10)
**Type:** execute | **Autonomous:** true

### Files
- `backend/requirements.txt` ← new
- `backend/Procfile` ← new
- `backend/.env.example` ← new
- `README.md` (project root) ← new

---

### Task 4.1 — Write `requirements.txt`

**File:** `backend/requirements.txt`

**Action:** Create `backend/requirements.txt` with these exact pinned versions (D-05):

```
fastapi==0.115.12
uvicorn[standard]==0.34.0
pydantic==2.9.2
pydantic-settings==2.7.0
openai==1.65.5
python-dotenv==1.0.1
```

**Pin rationale:**
- `fastapi==0.115.12` — minimum 0.115+ per tech stack spec; `0.115.12` is the latest stable in that series.
- `uvicorn[standard]` — `[standard]` extras include `websockets` and `httptools` for production performance.
- `pydantic==2.9.2`, `pydantic-settings==2.7.0` — must be compatible (pydantic v2 only).
- `openai==1.65.5` — minimum 1.65+ per spec; provides `AsyncOpenAI`.
- `python-dotenv` — required by `pydantic-settings` for `.env` file loading.

Railway's Nixpacks detects `requirements.txt` in the root of the configured service directory and runs `pip install -r requirements.txt` automatically.

**Verify:**
```bash
cd backend && pip install -r requirements.txt --dry-run 2>&1 | tail -5
```
No dependency conflicts.

**Done:** `requirements.txt` exists with all six packages, each with an exact version pin.

---

### Task 4.2 — Write `Procfile`

**File:** `backend/Procfile`

**Action:** Create `backend/Procfile` with exactly one line:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Rules:**
- `$PORT` — Railway injects this at runtime. Hardcoding `8000` would break deployment.
- `--host 0.0.0.0` — required; Railway's network layer cannot reach `127.0.0.1`.
- No `--reload` in production (only in local dev).
- Railway recognizes `Procfile` + `requirements.txt` as a Python service and uses the `web` process type.
- In the Railway project, set **Root Directory** to `backend/` so Railway reads `backend/Procfile`.

**Verify:** `cat backend/Procfile` outputs exactly the one-liner above.

**Done:** `Procfile` exists with the correct uvicorn start command.

---

### Task 4.3 — Write `.env.example`

**File:** `backend/.env.example`

**Action:** Create `backend/.env.example`:

```dotenv
# Copy this file to .env for local development.
# NEVER commit .env to git — it is already in .gitignore.

# Required — obtain from Railway dashboard or openai-hk.com account
OPENAI_API_KEY=your_openai_api_key_here

# Optional — defaults to https://api.openai-hk.com/v1
OPENAI_BASE_URL=https://api.openai-hk.com/v1

# CORS allowed origins.
# Dev: use * for convenience (D-06).
# Phase 3: set to comma-separated list, e.g. https://your-app.vercel.app,http://localhost:5173 (D-07)
ALLOWED_ORIGINS=*

# Available models as a JSON array (D-03, D-04).
# Each entry must have "id" (exact model ID) and "label" (display name).
# Update in Railway env vars to change model list without code changes.
AVAILABLE_MODELS=[{"id":"gpt-4o-mini","label":"GPT-4o Mini (fast)"},{"id":"gpt-4o","label":"GPT-4o (smart)"}]

# Debug route gate (D-08).
# MUST be false (or unset) on any public production deployment (D-10).
ENABLE_DEBUG_CHAT_COMPLETION=false
```

**Verify:** File exists; `grep -c "=" backend/.env.example` returns 5 (five variable assignments).

**Done:** `.env.example` documents all five env vars with inline comments.

---

### Task 4.4 — Write project `README.md`

**File:** `README.md` (repository root — NOT inside `backend/`)

**Action:** Create `README.md`:

```markdown
# AI Quiz Generator

Generate multiple-choice quizzes from a topic or uploaded document using OpenAI-compatible models.

## Repository Structure

```
backend/    # FastAPI backend (Python 3.11+)
frontend/   # React frontend (Vite + TypeScript) — added in Phase 3
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
uvicorn app.main:app --reload --port 8000
```

The server starts at `http://localhost:8000`.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | — | API key for the LLM proxy |
| `OPENAI_BASE_URL` | No | `https://api.openai-hk.com/v1` | LLM proxy base URL |
| `ALLOWED_ORIGINS` | No | `*` | CORS origins — `*` or comma-separated list |
| `AVAILABLE_MODELS` | No | two-model fallback | JSON array of `{"id","label"}` objects |
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
```

**Verify:**
- `test -f README.md && echo "README exists"`
- `grep -q "ENABLE_DEBUG_CHAT_COMPLETION=false" README.md && echo "production warning present"`

**Done:** `README.md` exists at repo root; contains the `ENABLE_DEBUG_CHAT_COMPLETION=false` production warning (satisfies D-10).

---

### Verification (Plan 04 complete)

```bash
ls -1 backend/requirements.txt backend/Procfile backend/.env.example README.md
grep "ENABLE_DEBUG_CHAT_COMPLETION=false" README.md
cat backend/Procfile
```

All four files present; Procfile contains `$PORT`; README contains production warning.

---

## Plan 01 — Scaffold FastAPI App with CORSMiddleware, `/health`, and `/api/models`

**Wave:** 2 | **Depends on:** Plan 02
**Objective:** Create the FastAPI application entry point with CORS middleware and two working read-only routes.
**Requirements:** BACK-01, BACK-02, BACK-03
**Type:** execute | **Autonomous:** true

### Files
- `backend/app/__init__.py` ← new (empty)
- `backend/app/routers/__init__.py` ← new (empty)
- `backend/app/models/__init__.py` ← new (empty)
- `backend/app/services/__init__.py` ← new (empty)
- `backend/app/routers/health.py` ← new
- `backend/app/routers/models.py` ← new
- `backend/app/main.py` ← new

---

### Task 1.1 — Create Python package `__init__.py` files

**Files:** `backend/app/__init__.py`, `backend/app/routers/__init__.py`, `backend/app/models/__init__.py`, `backend/app/services/__init__.py`

**Action:** Create the directory tree then create four empty files (zero bytes each). These mark the directories as Python packages. No imports, no docstrings, no code.

```bash
mkdir -p backend/app/routers backend/app/models backend/app/services
touch backend/app/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
```

**Verify:**
```bash
python3 -c "
import sys; sys.path.insert(0, 'backend')
import app, app.routers, app.models, app.services
print('packages OK')
" 
```
(Run from repo root with `PYTHONPATH=backend` or `cd backend && python3 -c "import app"`)

**Done:** All four `__init__.py` files exist.

---

### Task 1.2 — Implement `GET /health` router

**File:** `backend/app/routers/health.py`

**Action:** Create `backend/app/routers/health.py`:

```python
from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Liveness endpoint. Must respond in < 50ms — no blocking I/O. (BACK-02)"""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
```

**Response contract:** `{"status": "ok", "timestamp": "<ISO 8601 UTC string>"}`. No database calls, no file I/O, no external network calls — Railway uses this for health probes.

**Verify (after main.py exists):**
```bash
curl -s http://localhost:8000/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok'
assert 'T' in d['timestamp']  # ISO 8601 contains 'T' separator
print('health OK:', d['timestamp'])
"
```

**Done:** `/health` returns 200 with `{"status": "ok", "timestamp": "..."}`.

---

### Task 1.3 — Implement `GET /api/models` router

**File:** `backend/app/routers/models.py`

**Action:** Create `backend/app/routers/models.py`:

```python
from typing import Any

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models() -> dict[str, list[Any]]:
    """Return available model list from AVAILABLE_MODELS env var. (BACK-03, D-03)"""
    return {"models": settings.available_models}
```

**Response contract:** `{"models": [{"id": "gpt-4o-mini", "label": "GPT-4o Mini (fast)"}, {"id": "gpt-4o", "label": "GPT-4o (smart)"}]}`. Returns the list exactly as parsed from `AVAILABLE_MODELS` — no filtering, no transformation.

**Verify (after main.py exists):**
```bash
curl -s http://localhost:8000/api/models | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'models' in d
assert isinstance(d['models'], list)
assert len(d['models']) >= 2
assert all('id' in m and 'label' in m for m in d['models'])
print('models OK:', [m['id'] for m in d['models']])
"
```

**Done:** `/api/models` returns 200 with a `models` array containing objects with `id` and `label` fields.

---

### Task 1.4 — Create `main.py` — FastAPI app + CORSMiddleware + router wiring

**File:** `backend/app/main.py`

**Action:** Create `backend/app/main.py`:

```python
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Quiz Generator", version="0.1.0")

# CORSMiddleware MUST be added before include_router calls (BACK-01, D-06).
# Phase 1: ALLOWED_ORIGINS=* for dev convenience.
# Phase 3: tighten to Vercel URL + http://localhost:5173 (D-07).
# CRITICAL: allow_credentials=False is required when allow_origins=["*"].
#           FastAPI raises RuntimeError if allow_credentials=True with wildcard origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(models.router)

# Debug router is mounted conditionally in Plan 03. Do NOT add it here.
```

**Critical ordering rules (BACK-01):**
1. `app.add_middleware(CORSMiddleware, ...)` must appear **before** any `app.include_router(...)` call.
2. `allow_credentials=False` — mandatory when `allow_origins` includes `"*"`. FastAPI enforces this at startup.
3. `health.router` has no prefix (route is `/health`). `models.router` has `prefix="/api"` (route is `/api/models`).

**Verify:**
```bash
cd backend
OPENAI_API_KEY=test uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/models
# Both return JSON without errors
kill %1
```

**Done:** Server starts without errors. `/health` and `/api/models` both return 200. No CORS-related startup errors.

---

### Verification (Plan 01 complete)

```bash
cd backend
OPENAI_API_KEY=test uvicorn app.main:app --port 8000 &
sleep 2

curl -s http://localhost:8000/health | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='ok'"
curl -s http://localhost:8000/api/models | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d['models'])>=2"

# Verify CORS headers on preflight
curl -s -I -X OPTIONS http://localhost:8000/health \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" | grep -i "access-control-allow-origin"

kill %1
```

All three checks pass = Plan 01 complete.

---

## Plan 03 — Debug Route (`POST /api/debug/chat-completion`)

**Wave:** 3 | **Depends on:** Plans 01, 02
**Objective:** Implement the gated LLM smoke route that mounts only when `ENABLE_DEBUG_CHAT_COMPLETION=true`, uses an allowlisted model, and hard-caps tokens at 64.
**Requirements:** BACK-07
**Type:** execute | **Autonomous:** true

### Files
- `backend/app/routers/debug.py` ← new
- `backend/app/main.py` ← modified (add conditional router mount)

---

### Task 3.1 — Implement `debug.py` router

**File:** `backend/app/routers/debug.py`

**Action:** Create `backend/app/routers/debug.py`:

```python
from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api/debug")


class DebugChatRequest(BaseModel):
    model: str  # required; must be in AVAILABLE_MODELS allowlist (D-09)
    message: str = "Say hello in exactly three words."  # optional; short default


@router.post("/chat-completion")
async def debug_chat_completion(body: DebugChatRequest) -> dict[str, str]:
    """
    Gated LLM smoke test. Only mounted when ENABLE_DEBUG_CHAT_COMPLETION=true (D-08).
    Hard-caps max_tokens at 64. model must be in AVAILABLE_MODELS allowlist (D-09).
    WARNING: Disable on production (D-10).
    """
    if body.model not in settings.available_model_ids:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Model '{body.model}' is not in the AVAILABLE_MODELS allowlist. "
                f"Allowed: {sorted(settings.available_model_ids)}"
            ),
        )

    client = AsyncOpenAI(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
    )

    try:
        response = await client.chat.completions.create(
            model=body.model,
            messages=[{"role": "user", "content": body.message}],
            max_tokens=64,  # Hard cap — not configurable from request (D-09)
            temperature=0.7,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"LLM call failed: {exc}",
        ) from exc

    reply = response.choices[0].message.content or ""
    return {"reply": reply, "model_used": body.model}
```

**Contract (D-09):**
- Request: `{"model": "<string, required>", "message": "<string, optional>"}`.
- Response: `{"reply": "<assistant reply>", "model_used": "<model id>"}`.
- HTTP 400 if `model` not in `settings.available_model_ids`.
- HTTP 503 if LLM call raises any exception.
- `max_tokens=64` is hard-coded — not derived from request body.
- `AsyncOpenAI` (not `OpenAI`) — endpoint is `async def`; sync client would block the event loop.
- Client instantiated per-request (acceptable for a non-hot-path debug route).

**Verify (import check — no live LLM needed):**
```bash
cd backend
OPENAI_API_KEY=test python3 -c "
from app.routers.debug import router, DebugChatRequest
req = DebugChatRequest(model='gpt-4o-mini')
assert req.model == 'gpt-4o-mini'
assert req.message == 'Say hello in exactly three words.'
print('debug router imports OK')
"
```

**Done:** Module imports without error; `DebugChatRequest` validates `model` field; `router` has one POST route.

---

### Task 3.2 — Conditionally mount debug router in `main.py`

**File:** `backend/app/main.py`

**Action:** Append the following block to the bottom of the existing `main.py` (after the existing `include_router` calls):

```python
# Conditional debug router (D-08).
# When ENABLE_DEBUG_CHAT_COMPLETION=false (default), this block is skipped —
# the route does not exist and returns 404 automatically.
# WARNING: Keep ENABLE_DEBUG_CHAT_COMPLETION=false on production (D-10).
if settings.enable_debug_chat_completion:
    from app.routers import debug  # local import — only runs when gate is true
    app.include_router(debug.router)
    logger.warning(
        "Debug chat-completion route is ENABLED. "
        "Disable ENABLE_DEBUG_CHAT_COMPLETION before production deployment."
    )
```

**Critical rules:**
- The `import` is **inside** the `if` block — a top-level `from app.routers import debug` would cause the route to be registered regardless of the flag.
- When the flag is `False`, the route does not appear in the OpenAPI schema (`/docs`) or the routing table. It is completely absent — not a 404 handler.
- The `logger.warning(...)` reminds developers who enable the flag locally that it must be disabled before production.

**Verify:**
```bash
cd backend

# Flag off — route must NOT exist
OPENAI_API_KEY=test python3 -c "
from app.main import app
paths = [r.path for r in app.routes]
assert '/api/debug/chat-completion' not in paths, f'debug route must not exist, found: {paths}'
print('flag-off: route absent ✓')
"

# Flag on — route must exist
OPENAI_API_KEY=test ENABLE_DEBUG_CHAT_COMPLETION=true python3 -c "
from app.main import app
paths = [r.path for r in app.routes]
assert '/api/debug/chat-completion' in paths, f'debug route must exist, found: {paths}'
print('flag-on: route present ✓')
"
```

**Done:** Route is absent when flag is `false`/unset; present when flag is `true`.

---

### Verification (Plan 03 complete)

```bash
cd backend

# Start with flag enabled
OPENAI_API_KEY=<real_key> ENABLE_DEBUG_CHAT_COMPLETION=true uvicorn app.main:app --port 8000 &
sleep 2

# Live LLM call — requires real OPENAI_API_KEY
curl -s -X POST http://localhost:8000/api/debug/chat-completion \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","message":"Say hi in exactly two words."}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'reply' in d, f'missing reply: {d}'
assert d['model_used'] == 'gpt-4o-mini', f'wrong model: {d}'
print('debug route OK. Reply:', d['reply'])
"

# Confirm allowlist enforcement
curl -s -X POST http://localhost:8000/api/debug/chat-completion \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4-turbo","message":"test"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('detail','').startswith('Model'); print('allowlist enforcement OK')"

kill %1
```

---

## Plan 05 — Deploy to Railway + Set Environment Variables

**Wave:** 4 | **Depends on:** Plans 01, 02, 03, 04
**Objective:** Deploy the backend to Railway and configure all required environment variables so the app is publicly reachable at a stable URL.
**Requirements:** DEPLOY-01, DEPLOY-03
**Type:** checkpoint:human-action | **Autonomous:** false

### Tasks

#### Task 5.1 — Push code and create Railway project

**What Claude does first:**
```bash
git add backend/ README.md
git commit -m "feat(01): FastAPI backend scaffold with health, models, debug routes"
git push origin main
```

**What you (developer) must do in Railway:**

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
2. Select this repository.
3. In Railway project settings → **General** → **Root Directory** → enter `backend`.
4. Railway detects `Procfile` + `requirements.txt` and starts the first build automatically.
5. Watch build logs — confirm `pip install` completes without errors.
6. After the build, Railway shows a green deploy indicator.
7. Go to **Settings** → **Networking** → **Generate Domain** to get your public URL (e.g., `https://your-app-name.railway.app`).

**Done:** Railway shows green deploy; public URL is available.

---

#### Task 5.2 — Set environment variables in Railway dashboard

**In Railway:** Project → **Variables** tab → add each variable:

| Variable | Value to set |
|----------|-------------|
| `OPENAI_API_KEY` | Your openai-hk.com API key |
| `OPENAI_BASE_URL` | `https://api.openai-hk.com/v1` |
| `ALLOWED_ORIGINS` | `*` |
| `AVAILABLE_MODELS` | `[{"id":"gpt-4o-mini","label":"GPT-4o Mini (fast)"},{"id":"gpt-4o","label":"GPT-4o (smart)"}]` |
| `ENABLE_DEBUG_CHAT_COMPLETION` | `false` |

After adding all variables, Railway triggers an automatic redeploy. Wait for the redeploy to succeed (green indicator).

**Done:** All five variables are set in Railway; redeploy succeeds.

---

#### Task 5.3 — Verify live health endpoint

```bash
# Replace with your actual Railway URL
RAILWAY_URL=https://your-app-name.railway.app

curl -s "$RAILWAY_URL/health" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok'
assert 'timestamp' in d
print('health live OK:', d['timestamp'])
"

curl -s "$RAILWAY_URL/api/models" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert len(d['models']) >= 2
print('models live OK:', [m['id'] for m in d['models']])
"
```

**Done:** Both endpoints return 200 with correct JSON from the Railway URL.

---

**Resume signal:** Type `"deployed: https://your-railway-url.railway.app"` when health and models are confirmed live.

---

## Plan 06 — Smoke Test: CORS + Live Endpoint Verification

**Wave:** 5 | **Depends on:** Plan 05
**Objective:** Confirm CORS headers are correct from a real browser context, and optionally verify LLM connectivity via the debug route in a temporary staging configuration.
**Requirements:** BACK-01, BACK-07
**Type:** checkpoint:human-verify | **Autonomous:** false

### Tasks

#### Task 6.1 — Automated CORS preflight check

```bash
RAILWAY_URL=https://your-app-name.railway.app  # set to actual URL

curl -v -X OPTIONS "$RAILWAY_URL/health" \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" 2>&1 \
  | grep -i "access-control"
```

**Expected headers in response:**
```
access-control-allow-origin: *
access-control-allow-methods: *
access-control-allow-headers: *
```

**Done:** Preflight returns `access-control-allow-origin: *`.

---

#### Task 6.2 — Browser console CORS test

Open a browser dev console (any page — including `about:blank`) and run:

```javascript
fetch("https://your-app-name.railway.app/health")
  .then(r => r.json())
  .then(d => console.log("CORS OK:", d))
  .catch(e => console.error("CORS FAILED:", e));
```

**Expected:** Console prints `CORS OK: {status: "ok", timestamp: "..."}` — no CORS errors in console.

**Done:** `/health` is reachable cross-origin from browser without any CORS error.

---

#### Task 6.3 — Optional: debug route LLM connectivity check

> Only run this if you want to verify LLM connectivity before Phase 2.
> After testing, reset the flag to `false` and wait for Railway redeploy.

1. In Railway Variables: set `ENABLE_DEBUG_CHAT_COMPLETION=true` → wait for redeploy.
2. Run:

```bash
curl -s -X POST "$RAILWAY_URL/api/debug/chat-completion" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","message":"Reply with exactly the words: connection verified"}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'reply' in d, f'unexpected response: {d}'
print('LLM OK. Reply:', d['reply'])
print('Model used:', d['model_used'])
"
```

3. After verifying: set `ENABLE_DEBUG_CHAT_COMPLETION=false` in Railway Variables → wait for redeploy.

**Done:** Real assistant reply returned; `model_used` is `"gpt-4o-mini"`.

---

### Verification (Plan 06 complete)

- `curl -v OPTIONS` preflight shows `access-control-allow-origin: *`.
- Browser console `fetch()` to `/health` completes without CORS errors.
- (Optional) Debug route returns a real LLM reply.

**Resume signal:** Type `"smoke test passed"` with any notable observations (e.g., CORS header present, LLM reply received).

---

## Overall UAT Checklist

All five criteria must be TRUE to close Phase 1.

| # | Success Criterion | Verification Command / Action |
|---|-------------------|-------------------------------|
| **1** | `GET /health` at Railway URL returns HTTP 200 with timestamp | `curl -s $RAILWAY_URL/health` → `{"status":"ok","timestamp":"..."}` |
| **2** | `GET /api/models` returns configured model list as JSON | `curl -s $RAILWAY_URL/api/models` → `{"models":[...]}` with ≥ 2 objects, each with `id` + `label` |
| **3** | CORS middleware accepts requests from `*` origin | Browser `fetch("$RAILWAY_URL/health")` succeeds without CORS error in console |
| **4** | Railway env vars (`OPENAI_API_KEY`, `ALLOWED_ORIGINS`, `AVAILABLE_MODELS`) loaded | `/api/models` returns Railway-configured list; app starts without "field required" error for `OPENAI_API_KEY` |
| **5a** | When `ENABLE_DEBUG_CHAT_COMPLETION=true`: debug route exists and returns real LLM reply | `curl -X POST $RAILWAY_URL/api/debug/chat-completion -d '{"model":"gpt-4o-mini"}'` → `{"reply":"...","model_used":"gpt-4o-mini"}` |
| **5b** | When `ENABLE_DEBUG_CHAT_COMPLETION=false` (default): debug route is absent | `curl $RAILWAY_URL/api/debug/chat-completion` → HTTP 404 (route not mounted) |

Phase 1 is complete when all five rows pass.

---

## Must-Haves

```yaml
must_haves:
  truths:
    - "GET /health at the Railway URL returns HTTP 200 with a timestamp field"
    - "GET /api/models returns a JSON array of models with id and label fields"
    - "CORS preflight from any origin returns access-control-allow-origin: *"
    - "App starts without errors when OPENAI_API_KEY is set and AVAILABLE_MODELS is valid JSON"
    - "POST /api/debug/chat-completion exists and returns an LLM reply when flag is true"
    - "POST /api/debug/chat-completion does not exist at all when flag is false"

  artifacts:
    - path: "backend/app/config.py"
      provides: "Settings singleton with allowed_origins, available_models, available_model_ids, enable_debug_chat_completion"
      exports: ["settings"]

    - path: "backend/app/main.py"
      provides: "FastAPI app with CORSMiddleware + health + models routes; conditional debug mount"
      exports: ["app"]

    - path: "backend/app/routers/health.py"
      provides: "GET /health — returns status + ISO 8601 UTC timestamp"
      exports: ["router"]

    - path: "backend/app/routers/models.py"
      provides: "GET /api/models — returns settings.available_models"
      exports: ["router"]

    - path: "backend/app/routers/debug.py"
      provides: "POST /api/debug/chat-completion — allowlisted model, max_tokens=64, AsyncOpenAI"
      exports: ["router", "DebugChatRequest"]

    - path: "backend/requirements.txt"
      provides: "Pinned Python dependencies for Railway auto-install"
      contains: "fastapi, uvicorn, pydantic, pydantic-settings, openai, python-dotenv"

    - path: "backend/Procfile"
      provides: "Railway start command"
      contains: "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT"

    - path: "README.md"
      provides: "Setup instructions and production debug-route warning"
      contains: "ENABLE_DEBUG_CHAT_COMPLETION=false"

  key_links:
    - from: "backend/app/main.py"
      to: "app.config.settings.allowed_origins"
      via: "CORSMiddleware(allow_origins=settings.allowed_origins)"
      pattern: "add_middleware.*CORSMiddleware"

    - from: "backend/app/routers/models.py"
      to: "app.config.settings.available_models"
      via: "return {\"models\": settings.available_models}"
      pattern: "settings\\.available_models"

    - from: "backend/app/main.py"
      to: "app.routers.debug"
      via: "if settings.enable_debug_chat_completion: app.include_router(debug.router)"
      pattern: "enable_debug_chat_completion"

    - from: "backend/app/routers/debug.py"
      to: "openai.AsyncOpenAI"
      via: "AsyncOpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key)"
      pattern: "AsyncOpenAI"
```
