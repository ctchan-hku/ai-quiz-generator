# Phase 1: Backend Scaffold — Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Scaffold the FastAPI backend, configure the app for Railway deployment, expose `/health`, `/api/models`, and the gated `POST /api/debug/chat-completion`. No quiz generation logic yet — this phase ends with a publicly reachable backend that proves the stack and deployment pipeline work.

**In scope:**
- FastAPI app skeleton with CORS, health, and models routes
- pydantic-settings config loading env vars
- openai SDK installed and wired to debug route
- `POST /api/debug/chat-completion` behind feature flag
- requirements.txt + Railway deployment config
- Railway deploy and env var setup
- CORS smoke test from browser / curl

**Out of scope:**
- Any quiz generation logic (Phase 2)
- React frontend (Phase 3)
- File upload routes (Phase 4)
- Rate limiting (Phase 2 — first generate endpoint)
- Any persistence, auth, or user management

</domain>

<decisions>
## Implementation Decisions

### Repo Layout
- **D-01:** Monorepo — `backend/` and `frontend/` as sibling directories in this repository (single git history, easier cross-referencing for a solo/small team MVP).
- **D-02:** Inside `backend/`, use the structured layout: `backend/app/` with `routers/`, `services/`, and `models/` subfolders — matches the architecture design and keeps routes, business logic, and schemas separated from day one.

### Models List
- **D-03:** `AVAILABLE_MODELS` is a JSON array stored as a Railway environment variable (e.g. `[{"id":"gpt-4o-mini","label":"GPT-4o Mini (fast)"},{"id":"gpt-4o","label":"GPT-4o (smart)"}]`). Updating the list requires no code change — just a Railway env var update and redeploy.
- **D-04:** Offer a **range** — one fast/cheap model (GPT-4o-mini class) plus one smarter model (GPT-4o class). This gives users a meaningful choice in the dropdown without exposing a long list. Exact model IDs sourced from openai-hk.com pricing at deploy time.

### Dependency Tooling
- **D-05:** Use **`requirements.txt`** with `pip`. Railway auto-detects and installs without extra config files. Simple, battle-tested, and avoids any nixpacks/Procfile overhead for the MVP.

### CORS Strategy
- **D-06:** During **Phase 1** (no frontend yet), set `ALLOWED_ORIGINS=*` to allow unrestricted smoke testing from curl, Postman, or browser console against the live Railway URL. This is a temporary development convenience — note it in code comments.
- **D-07:** From **Phase 3 onward** (Vercel URL known), tighten `ALLOWED_ORIGINS` to two values: the Vercel production URL + `http://localhost:5173`. Delivered as a comma-separated Railway env var. Never use `*` in combination with `allow_credentials=True`.

### Debug Route
- **D-08:** `POST /api/debug/chat-completion` is included in Phase 1. The router is mounted **only when** `ENABLE_DEBUG_CHAT_COMPLETION=true` (env var, defaults to `false`). When the flag is false, the endpoint must not exist — not just return an error.
- **D-09:** The debug route uses the same `OPENAI_API_KEY` and `base_url` as the production LLM client. Request body: `model` (required, allowlisted against `AVAILABLE_MODELS`), optional `message` string. Server caps `max_tokens` hard at 64. Returns JSON: `{ "reply": "...", "model_used": "..." }`.
- **D-10:** README must document: "Set `ENABLE_DEBUG_CHAT_COMPLETION=false` (or leave unset) on any public production deployment."

### Claude's Discretion
- Exact FastAPI version, uvicorn options, and Python runtime version (target Python 3.11+, pin in requirements.txt).
- Whether to use a `Procfile` or `nixpacks.toml` for Railway — use whichever Railway auto-detects more reliably for standard FastAPI.
- Error response shape for debug route (400 if model not in allowlist, 503 if LLM unreachable).
- Logging setup (stdlib `logging` is fine; no structured logging required for MVP).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — vision, constraints, out-of-scope decisions
- `.planning/REQUIREMENTS.md` — full requirement list; BACK-01 to BACK-07 are Phase 1; see § Key Design Decisions Locked

### Architecture
- `.planning/research/ARCHITECTURE.md` — API endpoint designs (including `POST /api/debug/chat-completion`), CORS config, project directory structure (`/backend/main.py`, `routers/`, `services/`, `models/`, `config.py`)
- `.planning/research/STACK.md` — recommended libraries with versions (FastAPI 0.115+, pydantic-settings 2.x, openai SDK 1.65+, uvicorn[standard] 0.34+)

### Pitfalls
- `.planning/research/PITFALLS.md` — CORS misconfiguration (Pitfall 4), Railway cold start (Pitfall 5)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project, no existing code.

### Established Patterns
- None yet — Phase 1 establishes the patterns all subsequent phases will follow.

### Integration Points
- `backend/app/config.py` (created this phase) — all future services read env vars from here; Phase 2 will import `settings.openai_api_key` and `settings.openai_base_url`.
- `backend/app/routers/debug.py` (created this phase, gated) — pattern for how additional routers are registered in `main.py`.
- `backend/app/main.py` — the FastAPI app instance; Phase 2 adds `routers/generate.py` to this same file.

</code_context>

<specifics>
## Specific Ideas

- openai-hk.com is an OpenAI-compatible proxy — use `AsyncOpenAI(base_url="https://api.openai-hk.com/v1", api_key=settings.openai_api_key)`. The same client config is used in Phase 2 for quiz generation. Confirmed base URL from user-provided example: `https://api.openai-hk.com/v1` (NOT `www.openai-hk.com/v1`).
- The `AVAILABLE_MODELS` env var should parse as JSON so it can carry both `id` and `label` fields. A fallback hardcoded list is fine if the env var is absent in local dev.
- The debug route's allowlist check (`model` must be in `AVAILABLE_MODELS`) prevents cost surprises from arbitrary model names.

</specifics>

<deferred>
## Deferred Ideas

- Rate limiting on debug route — deferred to align with Phase 2 when `slowapi` is introduced. For now, the feature flag provides sufficient protection.
- Structured logging / log aggregation — out of scope for MVP; revisit if Railway log viewer proves insufficient.
- `pyproject.toml` + `uv` migration — noted as a v1.1 improvement; `requirements.txt` chosen for zero-config Railway deploy.

</deferred>

---

*Phase: 01-backend-scaffold*
*Context gathered: 2026-04-22*
