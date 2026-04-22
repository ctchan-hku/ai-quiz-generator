# Research Summary: AI Quiz Generator MVP

**Synthesized:** 2026-04-22
**Sources:** STACK.md · FEATURES.md · ARCHITECTURE.md · PITFALLS.md
**Overall Confidence:** HIGH — all four research areas have well-established patterns with multiple corroborating sources

---

## Executive Summary

This is a stateless AI-powered quiz generation web app: a user provides a topic or document, the backend calls an OpenAI-compatible LLM, and the frontend displays a structured multiple-choice quiz. The app is public (no auth), ephemeral (no persistence), and deployed as a split-deploy SPA (Vercel) + API (Railway). Every major technology decision has a clear rationale — FastAPI for async-native AI calls, React + Vite for lightweight SPA deployment, pypdf for zero-dependency PDF extraction, and TanStack Query for mutation-based async state.

The reference product is Jotform's AI Quiz Generator, and its 3-step flow (Input → Configure → Review & Export) is the correct UX pattern to replicate. The model selection dropdown is the only genuine differentiator at MVP — all other features are table stakes. The full feature set fits comfortably into a 7-phase build plan without requiring a single architectural pivot.

The most significant risks are not architectural — they're operational. An anonymous, public app with no rate limiting is one Reddit post away from a $500 OpenAI bill. Scanned PDFs silently return empty text, creating trust-destroying hallucinated quizzes. LLM JSON output must be validated with Pydantic regardless of `response_format` mode, because the openai-hk.com proxy cannot be trusted to enforce schema. Mitigations for all three are simple and well-documented — they must be built before any public URL is shared.

---

## Recommended Stack

| Layer | Technology | Version | Why |
|-------|-----------|---------|-----|
| Backend framework | FastAPI | 0.115+ | Async-native; auto OpenAPI docs; Pydantic integration |
| Python runtime | Python | 3.11+ | Best Pydantic v2 compatibility; perf gains over 3.10 |
| ASGI server | uvicorn[standard] | 0.34+ | Standard for FastAPI; Railway-compatible |
| Data validation | Pydantic v2 | 2.9+ | 5-50x faster than v1; validates LLM output schema |
| Config management | pydantic-settings | 2.x | Type-safe env var loading; IDE autocomplete |
| PDF extraction | pypdf | 5.x | Pure Python, MIT licensed, zero native deps |
| Async file I/O | aiofiles | 24.x | Non-blocking file reads in async endpoints |
| File upload parsing | python-multipart | 0.0.18+ | Required for FastAPI `UploadFile` — silent failure without it |
| AI client | openai | 1.65+ | Drop-in compatible with openai-hk.com via `base_url` |
| Frontend framework | React | 19.x | Concurrent features; React 19 Actions simplify forms |
| Type safety | TypeScript | 5.x | Catches API contract mismatches at compile time |
| Build tool | Vite | 6.x | Near-instant HMR; correct for split-deploy SPA pattern |
| CSS | Tailwind CSS | v4.x | No config file needed; fast iteration |
| Components | shadcn/ui | latest | Source-copied, Radix-based, accessible primitives |
| Async state | TanStack Query | v5.x | `useMutation` is the right primitive for generate→review flow |
| HTTP client | Axios | 1.7+ | Cleaner FormData + upload progress for mixed text/file requests |
| Python package mgr | uv | latest | 10-100x faster than pip; 2026 standard |
| Python linting | ruff | latest | Replaces flake8 + black + isort in one tool |
| Deployment (FE) | Vercel | — | Zero-config Vite React; stable `*.vercel.app` URL for CORS |
| Deployment (BE) | Railway | — | Auto-detects Python; env var panel; `$PORT` injection |

**Key exclusions:** No PyMuPDF (AGPL license risk), no Next.js (SSR complexity with no benefit for pure SPA), no Flask (sync-first), no Redux/Zustand (no global state needed), no CRA (unmaintained).

---

## Table Stakes Features

Everything in this list is required for the MVP. Users leave or distrust the product without them.

| # | Feature | Notes |
|---|---------|-------|
| 1 | **Topic prompt → quiz** | Primary entry point; text input + Generate button |
| 2 | **PDF / text file upload → quiz** | Secondary entry point; tabbed input UI |
| 3 | **Configurable question count** | Fixed options: 5 / 10 / 15 / 20 |
| 4 | **Multiple-choice output (4 options, 1 correct)** | Labeled A/B/C/D; `correct_indices: [i]` on `MultipleChoiceQuestion` (discriminated union) |
| 5 | **Model selection dropdown** | Populated from `/api/models`; our differentiator |
| 6 | **Loading / generation feedback** | Stepped states: "Uploading → Reading PDF → Generating questions" |
| 7 | **Review screen with answers visible** | Numbered questions; correct answer highlighted |
| 8 | **Clipboard copy** | Formatted plain text; zero-friction sharing |
| 9 | **JSON download** | Array of discriminated question objects (`question_type` + fields per variant); v1 only `multiple_choice` |
| 10 | **Error handling** | API failure, scanned PDF, empty prompt — all surfaced gracefully |
| 11 | **Empty state / example prompts** | Reduces blank-page paralysis on first visit |

**Defer to v1.1:** Streaming output (SSE), difficulty control, answer explanations on demand, individual question regeneration, True/False type.

**Defer to v2+:** URL/YouTube input, PDF export, quiz scoring/test mode, LMS integrations.

**Never build:** User accounts, quiz persistence, quiz scoring/response collection, collaborative editing, custom branding/themes.

---

## Architecture Overview

The app is a **split-deploy SPA + API** with no shared session state and no database.

```
Vercel (React SPA, static)
  QuizForm → QuizDisplay → ExportPanel
       │ HTTPS + CORS
Railway (FastAPI, uvicorn)
  POST /api/generate/text   (JSON body)
  POST /api/generate/file   (multipart/form-data)
  GET  /api/models          (model list, cached)
  GET  /health              (keepalive + health check)
       │
  Extraction Layer          pypdf (PDF) or UTF-8 decode (txt)
       │
  Prompt Builder            system_prompt + user_content → messages[]
       │
  LLM Client                AsyncOpenAI(base_url="https://api.openai-hk.com/v1")
       │
  Response Parser           json.loads → Pydantic QuizSchema validation
       │ QuizResponse JSON
Vercel ← Railway
```

**Two generate endpoints** (not one): `/generate/text` accepts JSON; `/generate/file` accepts multipart. Browsers cannot mix these content types in a single request — two endpoints is the correct design.

**Frontend state machine** uses `useReducer` with five explicit states: `idle → generating → reviewing → exporting → idle`. Form config (`topic`, `file`, `numQuestions`, `model`) is separate persistent state that survives regenerations.

**LLM call parameters:** `response_format: json_object`, `temperature: 0.7`, `max_tokens: 4096`, `timeout: 55s` (5s headroom before Railway's 60s limit).

**PDF truncation:** Text truncated to 12,000 chars (~3,000 tokens) for MVP. Inform user when truncation occurs. Chunking/sampling is a post-MVP enhancement.

**Pydantic schema:** discriminated union on `question_type` — `QuestionBase` (`question`, `explanation`), `OptionsQuestion` subclasses for MCQ/TF/multi-select (`options`, `correct_indices`), `ShortAnswerQuestion` (`expected_answer`). v1 LLM output matches `MultipleChoiceQuestion` only. See `.planning/REQUIREMENTS.md` § Question schema.

**Project structure:**
```
/backend/main.py              FastAPI app, CORS, routers
/backend/routers/generate.py  /api/generate/* endpoints
/backend/services/llm.py      prompt builder + LLM client + parser
/backend/services/extraction.py  PDF + text extraction
/backend/models/schemas.py    Pydantic models
/backend/config.py            env var settings
/frontend/src/components/     QuizForm, QuizDisplay, ExportPanel
/frontend/src/hooks/          useQuizMachine (useReducer)
/frontend/src/api/client.ts   typed Axios wrappers
```

---

## Top Pitfalls to Avoid

### CRITICAL — Must be addressed before public launch

**1. LLM returns invalid or schema-violating JSON**
The openai-hk.com proxy cannot be trusted to enforce schema — even with `response_format: json_object`. Always wrap LLM output in `try/except json.JSONDecodeError`, validate with Pydantic, and implement one automatic retry with a corrective re-prompt. Strip markdown fences before parsing (```` ```json ``` ````). Return HTTP 502 on unrecoverable parse failure.

**2. Scanned PDFs silently return empty text**
pypdf extracts zero text from image-based PDFs with no error raised. After extraction, count words: if `< 50 words` for a multi-page document, reject with a clear user message — `"This PDF appears to be scanned. Upload a text-based PDF."` Do not attempt OCR for MVP.

**3. Anonymous API abuse — runaway costs**
No auth means any bot can hammer `/generate`. Add IP-based rate limiting with `slowapi` (suggested: 3 requests/IP/hour) **before sharing any public URL**. Set `max_tokens` on every LLM call. Set a hard spending cap on the OpenAI account. Log estimated cost per request.

### MODERATE — Address during build

**4. CORS failure in production**
Load `ALLOWED_ORIGINS` from an environment variable. Add `CORSMiddleware` as the **first** middleware. Never combine `allow_origins=["*"]` with `allow_credentials=True`. Test explicitly against the production Vercel URL (`curl -H "Origin: https://..."`) before launch.

**5. Railway cold start kills first impressions**
Railway free/hobby tier sleeps after inactivity. Add a `/health` endpoint and ping it every 5 minutes via UptimeRobot (free). Show optimistic stepped loading states in the frontend immediately on form submit — do not wait for the first API response.

**6. Large PDFs silently cover only the first few pages**
Truncation without notification is a trust violation. Inform users when content was truncated: `"Your document was shortened to fit the model's context window."` For MVP, cap at 30 pages or 10MB and reject larger files with a clear error.

**7. openai-hk.com proxy feature gaps**
Do not rely on proxy-side schema enforcement. Test the full generation flow against the actual openai-hk.com endpoint in staging — not just against the official OpenAI API. Validate client-side regardless. Log raw LLM responses before parsing to surface proxy-specific error formats.

### MINOR — Low effort, high return

**8. Frozen spinner abandonment** — Show stepped status text (`"Uploading... → Extracting text... → Generating questions..."`) with a time estimate. Disable submit on click immediately.

**9. Multi-column / table PDFs produce garbled text** — Detect heuristically (very short average sentence length) and warn the user. Do not attempt to fix extraction in MVP.

**10. Hallucinated correct answers** — System prompt must include: `"All questions MUST be derived solely from the provided text."` Add a UI disclaimer: `"Verify answers against your source material."`

---

## Build Order

Based on architectural dependencies — each phase delivers a working, deployable increment.

| Phase | What Gets Built | Delivers |
|-------|----------------|----------|
| **1** | Backend scaffold: FastAPI app, CORS middleware, `/health`, `/api/models` | Deployable Railway backend; frontend can probe health |
| **2** | Topic generation: `POST /api/generate/text`, prompt builder, LLM client, Pydantic parser, rate limiting | Full LLM pipeline validated end-to-end; no file complexity yet |
| **3** | React frontend — topic flow: QuizForm (topic mode), `useReducer` state machine, QuizDisplay, error states | Full e2e happy path: type topic → generate → review quiz |
| **4** | File upload backend: `POST /api/generate/file`, pypdf extraction, word count guard, truncation | Backend supports both input modes; scanned PDF rejection built |
| **5** | File upload frontend: tabbed input, file picker, multipart submit | QuizDisplay already built — reused unchanged |
| **6** | Export: JSON download, clipboard copy, ExportPanel | Pure frontend; no backend changes |
| **7** | Model selection UI: dropdown from `/api/models`, wired to requests | Quick UI addition; backend already supports it from Phase 1 |

**Phase 2 before Phase 3** — validate the LLM pipeline before adding file complexity. Phase 3 can begin in parallel once the Phase 2 endpoint is deployed.

**Rate limiting** (Pitfall 3) must land in Phase 2 before any public URL is shared. CORS validation (Pitfall 4) must be tested at Phase 1 deployment.

---

## Open Questions

Decisions to make before planning begins:

| # | Question | Options | Recommendation |
|---|----------|---------|---------------|
| 1 | **Which models appear in the dropdown?** | Hardcoded list in env var vs. live `/v1/models` from openai-hk.com | Hardcode for MVP — live fetch risks key exposure and adds startup dependency |
| 2 | **Rate limit threshold?** | 3 req/IP/hour (conservative) vs. 10/hour (permissive) vs. none until needed | Start at 3/hour; adjust after real usage data |
| 3 | **PDF size limit for MVP?** | 10MB file size limit vs. 30-page limit vs. both | Enforce both: 10MB upload cap + 30-page rejection with clear error |
| 4 | **Include `explanation` field in the quiz schema?** | Yes (ARCHITECTURE.md includes it) vs. defer to v1.1 (FEATURES.md says defer) | Include — it's already in the Pydantic schema and system prompt; cost is negligible |
| 5 | **Deployment timing for rate limiting?** | Ship rate limiting in Phase 2 vs. add just before public launch | Phase 2 — the endpoint is public the moment it's deployed to Railway |
| 6 | **Multi-column PDF handling?** | pypdf only (warn on bad output) vs. add pdfplumber for layout | pypdf only for MVP — add pdfplumber in v1.1 if user complaints emerge |

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|-----------|-------|
| Stack | HIGH | Official docs (FastAPI, OpenAI SDK, TanStack Query) + 2026-current sources |
| Features | HIGH | Direct analysis of 4 live competitor products (Jotform, Quizgecko, QuizWhiz, involve.me) |
| Architecture | HIGH | Standard FastAPI + OpenAI SDK idioms; verified against official docs |
| Pitfalls | HIGH | Multiple independent sources; real incident reports for cost abuse; official OpenAI proxy behavior docs |

**No significant gaps identified.** The research covers all major risk areas. The openai-hk.com proxy behavior cannot be verified without live testing — this is the only unknown, and the mitigation (client-side Pydantic validation) is already established.

---

## Sources Aggregated

- FastAPI official docs (fastapi.tiangolo.com) — CORS, file upload, middleware
- OpenAI Python SDK (github.com/openai/openai-python) — AsyncOpenAI, json_object mode
- TanStack Query v5 migration guide (tanstack.com)
- pypdf benchmark repo (github.com/py-pdf/benchmarks)
- Tailwind CSS v4 migration guide (digitalapplied.com, Jan 2026)
- Jotform AI Quiz Generator (jotform.com/ai/quiz-generator/) — reference UX
- Quizgecko, QuizWhiz, involve.me — competitor feature analysis
- LLM rate limiting and cost abuse (oneuptime.com/blog, sourcery.ai/security)
- Railway deployment troubleshooting (docs.railway.com)
- OpenAI Structured Outputs reliability (OpenAI Community)
- PDF extraction comparison 2025 (medium.com/@umesh382.kushwaha)
- LLM provider quirks (futuresearch.ai)
