# Phase 1: Backend Scaffold — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `01-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 01-backend-scaffold
**Areas discussed:** Repo Layout, Models List, Dependency Tooling, CORS Strategy, Debug Route

---

## Repo Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Monorepo (`backend/` + `frontend/`) | Single git history, easier cross-referencing | ✓ |
| Separate repos | More isolation, separate deploy histories | |
| Backend at root, `frontend/` subfolder | Slightly unusual layout | |

**User's choice:** Monorepo

| Option | Description | Selected |
|--------|-------------|----------|
| Structured (`backend/app/` with `routers/`, `services/`, `models/`) | Matches architecture design | ✓ |
| Flat (all files directly in `backend/`) | Simpler for MVP, refactor later | |

**User's choice:** Structured

---

## Models List

| Option | Description | Selected |
|--------|-------------|----------|
| JSON array in `AVAILABLE_MODELS` env var | Update without code change | ✓ |
| Hardcoded in `config.py` | Zero deploy config needed | |
| Live fetch from openai-hk.com `/v1/models` | Always current, risks key exposure | |

**User's choice:** JSON env var

| Option | Description | Selected |
|--------|-------------|----------|
| Cost-efficient only (fast/cheap model only) | Keeps bills minimal | |
| A range (one fast/cheap + one smarter) | Meaningful user choice, controlled cost ceiling | ✓ |
| Full curated list from openai-hk.com pricing | Maximum flexibility | |

**User's choice:** A range (fast + smart)

---

## Dependency Tooling

| Option | Description | Selected |
|--------|-------------|----------|
| `requirements.txt` | Railway auto-detects, zero config | ✓ |
| `pyproject.toml` + `uv` | 10-100x faster installs, needs nixpacks config | |

**User's choice:** `requirements.txt`

---

## CORS Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Allow `*` temporarily during Phase 1 | Easy smoke testing before Vercel URL exists | ✓ |
| `localhost:5173` only from day one | Stricter but limits manual testing | |

**User's choice for Phase 1:** Allow `*`

| Option | Description | Selected |
|--------|-------------|----------|
| Vercel production URL + `http://localhost:5173` | Both prod and local dev work | ✓ |
| Vercel production URL only | Strictest; local dev needs a proxy | |

**User's choice from Phase 3 onward:** Vercel URL + localhost:5173

---

## Debug Route

Arose during discussion of post-Phase-1 testability. User asked for a route that makes a real LLM call and returns a real assistant reply.

| Option | Description | Selected |
|--------|-------------|----------|
| `POST /api/debug/chat-completion` — real completion, gated by env flag | Proven connectivity to openai-hk.com before quiz logic exists | ✓ |
| No debug route in Phase 1 | Simpler; test in Phase 2 with actual quiz endpoint | |

**User's choice:** Include debug route in Phase 1
**Route name:** `POST /api/debug/chat-completion`
**Notes:** Gated by `ENABLE_DEBUG_CHAT_COMPLETION=true`; caps `max_tokens` at 64; model must be in `AVAILABLE_MODELS` allowlist; README note to keep off on public production.

---

## Claude's Discretion

- Exact Python + FastAPI + uvicorn version pins
- `Procfile` vs `nixpacks.toml` for Railway (whichever auto-detects cleanly)
- Error shape for debug route (400 if bad model, 503 if LLM unreachable)
- Logging setup (stdlib `logging`)

## Deferred Ideas

- Rate limiting on debug route — aligned with Phase 2 `slowapi` introduction
- Structured logging — post-MVP
- `pyproject.toml` + `uv` — noted for v1.1 improvement
