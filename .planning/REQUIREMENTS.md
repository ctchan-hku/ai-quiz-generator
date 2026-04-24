# Requirements — AI Quiz Generator MVP

**Version:** v1 (MVP)
**Last updated:** 2026-04-24 (FE-02: question count 0–10 per backend; model list from `/api/models`)
**Status:** Approved — ready for roadmap

---

## Question schema (API contract)

Questions are a **Pydantic discriminated union** on `question_type` (the discriminator). Shared fields live on bases; type-specific fields exist only on the variant that needs them — no `None` placeholders for “unused” fields.

**Class hierarchy (backend)**

| Layer | Classes | Shared fields |
|-------|---------|---------------|
| Root | `QuestionBase` | `question: str`, `explanation: str` |
| Options branch | `OptionsQuestion(QuestionBase)` | `options: list[str]`, `correct_indices: list[int]` |
| Variants | `MultipleChoiceQuestion`, `TrueFalseQuestion`, `MultiSelectQuestion` | Each sets `question_type: Literal[...]`; per-class `@model_validator` enforces option counts and index rules (e.g. MCQ: 4 options, exactly one correct index; TF: 2 options, one index; multi-select: ≥2 correct indices) |
| Free-text branch | `ShortAnswerQuestion(QuestionBase)` | `question_type: Literal["short_answer"]`, `expected_answer: str` (no `options` / `correct_indices`) |

**Union type:** `QuizQuestion = Annotated[MultipleChoiceQuestion | TrueFalseQuestion | MultiSelectQuestion | ShortAnswerQuestion, Field(discriminator="question_type")]`

**v1 generation:** The LLM and system prompt emit **only** `multiple_choice` items. Other variants are validated if present (e.g. manual API tests) but are not generated until v2.

**Frontend:** Mirror the same discriminated union in TypeScript (`switch (q.question_type)`) so rendering and export stay exhaustive.

---

## v1 Requirements

### BACK — Backend Infrastructure

- [x] **BACK-01**: FastAPI app with `CORSMiddleware` configured from `ALLOWED_ORIGINS` env var (Vercel domain)
- [x] **BACK-02**: `GET /health` endpoint returns 200 + timestamp for uptime monitoring
- [x] **BACK-03**: `GET /api/models` returns hardcoded list of available openai-hk.com model IDs and display names (sourced from env var or config)
- [x] **BACK-04**: `POST /api/generate/text` accepts JSON body `{topic, num_questions, model}` and returns a `QuizResponse`
- [x] **BACK-06**: IP-based rate limiting via `slowapi` — 3 requests/IP/hour — applied to all public generate endpoint(s) before any public URL is shared (`/text` in v1; add `/file` when upload ships)
- [x] **BACK-07**: `POST /api/debug/chat-completion` — optional **manual LLM smoke test** (real upstream call, real assistant reply). Router mounted only when `ENABLE_DEBUG_CHAT_COMPLETION=true` (default off). Body: `model` (required, must match an id from `AVAILABLE_MODELS`), optional `message` (short user text; server applies a low `max_tokens` cap e.g. ≤64). Uses same `OPENAI_API_KEY` and `base_url` as production client. Returns JSON with assistant text and `model_used`. Document in README that this must stay **disabled on production** unless intentionally used with care.

### AI — LLM Integration

- [x] **AI-01**: Prompt builder assembles `system_prompt` (schema instructions + constraints) and `user_content` (topic or extracted text) into `messages[]`
- [x] **AI-02**: LLM called via `AsyncOpenAI(base_url="https://api.openai-hk.com/v1")` with `response_format="json_object"`, `temperature=0.7`, `max_tokens=4096`, `timeout=55s`
- [x] **AI-03**: Response validated with Pydantic — `QuizSchema` wraps `questions: list[QuizQuestion]` where `QuizQuestion` is a **discriminated union** on `question_type`; implement `QuestionBase`, `OptionsQuestion`, `MultipleChoiceQuestion`, `TrueFalseQuestion`, `MultiSelectQuestion`, `ShortAnswerQuestion` with per-variant validators (no optional fields used as stand-ins for “not applicable”)
- [x] **AI-04**: v1 system prompt instructs the LLM to output only objects with `question_type: "multiple_choice"` (plus `question`, `options` length 4, `correct_indices` length 1, `explanation`); JSON shape in prompt must match `MultipleChoiceQuestion` exactly
- [x] **AI-05**: Auto-retry once with corrective re-prompt on `JSONDecodeError` or Pydantic validation failure; return HTTP 502 on second failure

### FE — Frontend

- [x] **FE-02**: Configuration panel — question count **0–10** (aligned with backend `GenerateTextRequest`) and model selector populated from `GET /api/models` (native `<select>` + TanStack Query in app)
- [x] **FE-03**: `useReducer` state machine with five explicit states: `idle → generating → reviewing → exporting → idle`
- [x] **FE-04**: Stepped loading feedback shown immediately on submit — at minimum "Generating questions…" before first response byte; upload flow prepends "Uploading… → Extracting text…" when document upload ships (v2)
- [x] **FE-05**: Quiz review screen — numbered questions, options labeled A/B/C/D, correct answer(s) highlighted, explanation shown below each question
- [x] **FE-06**: Empty state with 3 example topic prompts to reduce blank-page paralysis on first visit
- [x] **FE-07**: Graceful error display for: API failure, empty prompt, rate limit hit; file/scanned-PDF errors when upload exists (v2)

### EXP — Export

- [ ] **EXP-01**: "Copy to clipboard" button — formats quiz as readable plain text (question + options + answer key)
- [ ] **EXP-02**: "Download JSON" button — downloads the `questions[]` array as a `.json` file

### DEPLOY — Deployment & Operations

- [x] **DEPLOY-01**: Backend deployed and publicly reachable on Railway; `$PORT` used for uvicorn binding
- [x] **DEPLOY-02**: Frontend deployed and publicly reachable on Vercel; `VITE_API_BASE_URL` env var points to Railway backend URL
- [x] **DEPLOY-03**: `OPENAI_API_KEY`, `ALLOWED_ORIGINS`, and `AVAILABLE_MODELS` set as Railway environment variables — no secrets in code

---

## v2 Requirements (deferred)

### Document upload track *(removed from v1 roadmap 2026-04-24)*

- [ ] **BACK-05**: `POST /api/generate/file` accepts multipart form `{files: list[UploadFile], extra_context?, num_questions, model}` — designed for one or more files; UI may send one file initially
- [ ] **UPLOAD-01**: PDF text extracted via `pypdf` — `PdfReader(io.BytesIO(content))`, text joined page-by-page
- [ ] **UPLOAD-02**: Plain text files (`.txt`) decoded as UTF-8
- [ ] **UPLOAD-03**: Extracted text from all uploaded files concatenated with `\n\n---\n\n` separator before passing to prompt builder
- [ ] **UPLOAD-04**: Optional `extra_context` text field (from `/generate/file` multipart) prepended to extracted document text — enables combining typed notes with an uploaded document
- [ ] **UPLOAD-05**: Scanned PDF detection — if extracted word count < 50 for a multi-page PDF, reject with user-facing message: "This PDF appears to be scanned. Please upload a text-based PDF."
- [ ] **UPLOAD-06**: Combined extracted text truncated to 12,000 chars with user notification when truncation occurs
- [ ] **UPLOAD-07**: File upload size capped at 10MB per file; files with more than 30 pages rejected with clear error
- [ ] **FE-01**: Tabbed input panel — "Topic" tab (text prompt field) and "Upload" tab (single-file picker initially; backend already supports multiple files)

- Multi-file picker UI (single file first; backend already supports list)
- Enable LLM generation for `true_false`, `multiple_select`, and `short_answer` (schema and union members already exist; add prompt + UI renderers per variant)
- Difficulty level selector (easy / medium / hard) — prompt param only
- Answer explanations toggle (show/hide) — already in schema, just hide in v1 UI
- Individual question regeneration
- PDF export of quiz
- Streaming output via SSE (skeleton loading per question)
- pdfplumber fallback for multi-column/table PDFs

## Out of Scope

- User accounts / authentication — anonymous-only; saves complexity and removes friction for demos
- Quiz response collection / scoring / test mode — generation tool only
- Quiz persistence / history — stateless; each session is independent
- Custom branding or themes — plain functional UI
- URL or YouTube input — text/file only for v1
- OCR for scanned PDFs — reject with message instead; OCR adds native dependencies
- DOCX file support — text and PDF only for v1

---

## Key Design Decisions Locked

| Decision | Rationale |
|----------|-----------|
| Discriminated union on `question_type` | Parser and TypeScript narrow by tag; impossible shapes are unrepresentable |
| `QuestionBase` + `OptionsQuestion` + per-variant classes | Shared `question` / `explanation`; options-bearing types share `options` + `correct_indices`; `ShortAnswerQuestion` uses `expected_answer` only — no `None` fields for unused slots |
| `correct_indices: list[int]` on options variants | MCQ/TF: length 1; multi-select: length ≥2 — one field, variant-specific validation |
| `question_type` literals per class | `MultipleChoiceQuestion`, `TrueFalseQuestion`, `MultiSelectQuestion`, `ShortAnswerQuestion` each carry their own `Literal[...]` for Pydantic `Field(discriminator=...)` |
| `files: list[UploadFile]` on backend (v1 UI sends one) | Adding multi-file is a pure frontend change; backend already handles the list |
| `extra_context` optional field on `/generate/file` | Allows combining typed notes + uploaded document without a new endpoint |
| Two generate endpoints not one | Browsers cannot mix JSON and multipart in one request; two endpoints is correct design |
| Hardcoded model list in env var | Live `/v1/models` fetch risks key exposure and adds a startup dependency |
| Rate limiting before public URL | anonymous app = no billing firewall; 3 req/IP/hour added in Phase 2 |
| Debug chat-completion gated by env | `POST /api/debug/chat-completion` only when `ENABLE_DEBUG_CHAT_COMPLETION=true`; low `max_tokens`; off by default for public deploys |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 | Phase 1: Backend Scaffold | Complete |
| BACK-02 | Phase 1: Backend Scaffold | Complete |
| BACK-03 | Phase 1: Backend Scaffold | Complete |
| BACK-04 | Phase 2: AI Generation Pipeline | Complete |
| BACK-06 | Phase 2: AI Generation Pipeline | Complete |
| BACK-07 | Phase 1: Backend Scaffold | Complete |
| AI-01 | Phase 2: AI Generation Pipeline | Complete |
| AI-02 | Phase 2: AI Generation Pipeline | Complete |
| AI-03 | Phase 2: AI Generation Pipeline | Complete |
| AI-04 | Phase 2: AI Generation Pipeline | Complete |
| AI-05 | Phase 2: AI Generation Pipeline | Complete |
| FE-02 | Phase 4: Model Selection UI | Complete |
| FE-03 | Phase 3: React Frontend — Topic Flow | Complete |
| FE-04 | Phase 3: React Frontend — Topic Flow | Complete |
| FE-05 | Phase 3: React Frontend — Topic Flow | Complete |
| FE-06 | Phase 3: React Frontend — Topic Flow | Complete |
| FE-07 | Phase 3: React Frontend — Topic Flow | Complete |
| EXP-01 | Phase 5: Export | Pending |
| EXP-02 | Phase 5: Export | Pending |
| DEPLOY-01 | Phase 1: Backend Scaffold | Complete |
| DEPLOY-02 | Phase 3: React Frontend — Topic Flow | Complete |
| DEPLOY-03 | Phase 1: Backend Scaffold | Complete |

*Deferred to v2 (no v1 phase): BACK-05, UPLOAD-01 … UPLOAD-07, FE-01 — see **v2 Requirements**.*
