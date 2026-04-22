# Technology Stack

**Project:** AI Quiz Generator MVP
**Researched:** 2026-04-22
**Overall confidence:** HIGH

---

## Backend

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11+ | Runtime | 3.11 offers significant perf gains over 3.10; 3.12 available but 3.11 has broader ecosystem compatibility. Avoid 3.10 — Pydantic v2 type annotations work best on 3.11+. |
| FastAPI | 0.115+ | ASGI web framework | Async-native, auto-generates OpenAPI docs, typed request/response via Pydantic. Flask/Django are sync-first — unsuitable for async AI calls. Starlette (FastAPI's base) is too low-level. |
| uvicorn | 0.34+ | ASGI server | The standard ASGI server for FastAPI. Use `uvicorn[standard]` for production extras (watchfiles, httptools). |
| Pydantic | v2 (2.9+) | Data validation | Ships with FastAPI. v2 is 5-50x faster than v1 due to Rust core. All request/response models use Pydantic. |
| pydantic-settings | 2.x | Environment config | Type-safe `BaseSettings` class reads from `.env` and environment variables automatically. Preferred over raw `os.getenv()` — gives IDE autocomplete and validation at startup. |

### File Handling

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| python-multipart | 0.0.18+ | multipart/form-data parsing | Required by FastAPI's `UploadFile`. Without it, file upload endpoints silently fail. Install this or uploads won't work. |
| pypdf | 5.x | PDF text extraction | Pure-Python, MIT license, zero native dependencies — no compilation issues on Railway. For MVP quiz generation from well-formed PDFs (not scanned), pypdf's text extraction is sufficient. PyMuPDF is faster but AGPL-licensed (requires paid commercial license for closed-source use). |
| aiofiles | 24.x | Async file I/O | Required for async streaming of uploaded files to disk. Prevents blocking the event loop during large file writes. |

**Why NOT PyMuPDF:** AGPL-3.0 license requires any software using it to also be open-source, or purchase a commercial license. For a potentially commercialized product, pypdf (MIT) eliminates this legal risk. If OCR or complex layout handling becomes a requirement later, switch to PyMuPDF or Docling.

**Why NOT pdfminer.six / pdfplumber:** Slower than pypdf for basic text extraction. pdfplumber is useful for table detection — not needed for quiz generation from narrative text.

### AI Integration

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| openai | 1.65+ | AI API client | Drop-in compatible with openai-hk.com endpoint. Use `base_url` constructor param. The `OPENAI_BASE_URL` env var also works but explicit `base_url` in code is clearer for custom endpoints. |

```python
# backend/app/core/ai_client.py
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url="https://api.openai-hk.com/v1",  # confirmed base URL from openai-hk.com example
)
```

Use `AsyncOpenAI` (not `OpenAI`) since FastAPI endpoints are async. Mixing sync OpenAI client in async endpoints blocks the event loop.

### Backend Dependencies (requirements.txt)

```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
pydantic>=2.9.0
pydantic-settings>=2.5.0
python-multipart>=0.0.18
openai>=1.65.0
pypdf>=5.0.0
aiofiles>=24.1.0
python-dotenv>=1.0.0
```

---

## Frontend

### Core Stack

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| React | 19.x | UI framework | Concurrent features (useTransition) useful for AI response streaming UI. React 19 Actions simplify form handling. |
| TypeScript | 5.x | Type safety | Catches API contract mismatches at compile time. The `react-ts` Vite template is the standard starting point in 2026. |
| Vite | 6.x | Build tool / dev server | Near-instant HMR (50–200ms). CRA is dead. Next.js adds SSR complexity with no benefit for a pure SPA backed by a separate API server — Vite is correct for this split-deploy pattern. |
| Tailwind CSS | v4.x | Utility-first CSS | v4 eliminates `tailwind.config.js` — use `@import "tailwindcss"` in CSS and `@tailwindcss/vite` plugin. No PostCSS config needed. |
| shadcn/ui | latest | Component library | Copies source into your project (no version lock-in). Built on Radix UI primitives. Provides accessible, unstyled-by-default components (Button, Select, Card, etc.) that work with Tailwind v4. |

### Data Fetching

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| TanStack Query | v5.x | Server state / async state | Manages loading/error/success states for quiz generation and file uploads. `useMutation` is the right primitive for the "submit → generate" pattern. Caching is irrelevant here (no repeated fetches) but state management is the value. |
| Axios | 1.7+ | HTTP client | Preferred over native `fetch` for file uploads: cleaner `FormData` handling, upload progress events (`onUploadProgress`), automatic JSON response parsing. For a mostly-JSON backend, either works, but Axios is simpler for the mixed text+file upload use case. |

### Frontend Dependencies (package.json)

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "tailwindcss": "^4.0.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0"
  }
}
```

shadcn/ui is installed via CLI (`npx shadcn@latest init`) and adds components to `src/components/ui/` — no package.json entry.

---

## AI Integration

### Prompt Strategy

Structure the OpenAI request to return JSON directly rather than parsing markdown:

```python
response = await client.chat.completions.create(
    model=model_name,  # from user selection dropdown
    messages=[
        {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"},  # forces JSON output
    temperature=0.7,
)
```

Use `response_format={"type": "json_object"}` to avoid regex-parsing markdown fences. Not all openai-hk.com models may support this — fall back to prompt-engineering ("respond only with valid JSON") if the endpoint returns a 400 error on `response_format`.

### Model Listing

The model selection dropdown should be populated by calling the `/v1/models` endpoint on openai-hk.com. Cache the list on the backend at startup or with a short TTL — don't hit the models endpoint on every page load.

---

## File Processing

### PDF Upload Flow

```
Frontend: FileInput → FormData → POST /api/quiz/generate (multipart)
Backend:  UploadFile → read bytes → pypdf.PdfReader → extract text → truncate → AI prompt
```

**Size limit:** Enforce 10MB max on the backend (Railway free tier memory is ~512MB). Reject larger files with HTTP 413.

**Text truncation:** LLM context windows are finite. Truncate extracted text to ~12,000 tokens (~48,000 characters) before passing to the AI. Add a warning to the API response if content was truncated.

**Plain text files:** Accept `.txt` in addition to `.pdf`. Read directly as UTF-8. No library needed.

```python
async def extract_text(file: UploadFile) -> str:
    content = await file.read()
    if file.content_type == "application/pdf":
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return content.decode("utf-8", errors="replace")
```

---

## Deployment

### Split-Deploy Architecture

```
Vercel (frontend)          Railway (backend)
─────────────────          ─────────────────
React SPA (static)  ───►  FastAPI (uvicorn)
VITE_API_URL env var       OPENAI_API_KEY env var
                           ALLOWED_ORIGINS env var
```

### CORS Configuration (Backend)

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # list from env var
    allow_credentials=False,   # no cookies/auth — False avoids wildcard restriction
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**`ALLOWED_ORIGINS` env var:** Set to `https://your-app.vercel.app` in production. For local dev, include `http://localhost:5173`. Never hardcode — Railway env vars panel is the source of truth.

**Why `allow_credentials=False`:** The app has no auth. Setting `False` allows `allow_origins=["*"]` during development without the restriction that `allow_credentials=True` imposes (which prohibits wildcard origins).

### Environment Variables

**Backend (Railway Variables tab):**
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai-hk.com/v1
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
PORT=8000  # Railway sets this automatically
```

**Frontend (Vercel Environment Variables):**
```
VITE_API_URL=https://your-backend.railway.app
```

Vite requires the `VITE_` prefix for env vars exposed to the browser bundle. Access via `import.meta.env.VITE_API_URL` in TypeScript.

### Railway Configuration (backend)

Railway auto-detects Python apps. Provide a `Procfile` or `railway.toml`:

```
# Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Vercel Configuration (frontend)

Zero-config for Vite React apps. Vercel auto-detects Vite and runs `npm run build`. Outputs to `dist/`. Add a `vercel.json` only if you need SPA routing rewrites:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

---

## Dev Tooling

| Tool | Purpose | Why |
|------|---------|-----|
| `uv` | Python package manager | 10-100x faster than pip. `uv sync` installs from `pyproject.toml` or `requirements.txt`. Use `uv venv` for virtualenv. Rapidly becoming the 2026 standard. |
| ESLint + `@typescript-eslint` | TypeScript linting | Catches type errors the compiler misses in JSX context. Vite scaffolds this by default. |
| Prettier | Code formatting | Single formatter across TS/CSS/JSON. Agree on format once, never debate again. |
| Python `ruff` | Python linting + formatting | Replaces flake8 + black + isort in one fast tool. Use `ruff check` + `ruff format`. |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend framework | FastAPI | Flask | Flask is sync-first; blocking on AI API calls without threads. FastAPI's async is cleaner for this use case. |
| Backend framework | FastAPI | Django | Django is a full-stack framework with ORM, admin, templates — overkill for a pure JSON API with no persistence. |
| Frontend scaffold | Vite | Next.js | Next.js SSR/RSC adds complexity with no benefit; backend is already a separate API server. Vite is simpler and the correct choice for a SPA. |
| Frontend scaffold | Vite | CRA | Create React App is unmaintained since 2023. Do not use. |
| PDF library | pypdf | PyMuPDF | PyMuPDF is faster but AGPL-licensed — legal risk for commercial use. pypdf is MIT and sufficient for well-formed PDFs. |
| PDF library | pypdf | pdfminer.six | Slower for basic text extraction, more complex API. Only needed for layout-sensitive documents. |
| CSS | Tailwind v4 | CSS Modules | Tailwind v4 is faster to iterate. No context switching between CSS files and component markup. |
| HTTP client (frontend) | Axios | native fetch | Fetch requires manual `FormData` wrangling and lacks built-in upload progress. Axios is cleaner for mixed text+file requests. |
| State management | TanStack Query | Redux / Zustand | No persistent global state needed — all state is per-quiz-generation request. TanStack Query's `useMutation` covers the use case cleanly. |

---

## Sources

- FastAPI docs (fastapi.tiangolo.com) — MEDIUM confidence (checked Jan 2026 best practices article)
- PyPI benchmarks (github.com/py-pdf/benchmarks) — HIGH confidence (official benchmark repo)
- unstract.com PDF library evaluation 2026 — MEDIUM confidence (third-party, current year)
- medium.com Vite+shadcn guide Mar 2026 — MEDIUM confidence (current, multiple sources agree)
- Tailwind CSS v4 migration guide (digitalapplied.com Jan 2026) — MEDIUM confidence
- OpenAI Python SDK GitHub README — HIGH confidence (official)
- FastAPI CORS docs (fastapi.tiangolo.com/tutorial/cors/) — HIGH confidence (official)
- TanStack Query v5 migration guide (tanstack.com) — HIGH confidence (official)
