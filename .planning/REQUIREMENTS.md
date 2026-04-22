# Requirements — AI Quiz Generator MVP

**Version:** v1 (MVP)
**Last updated:** 2026-04-22
**Status:** Approved — ready for roadmap

---

## v1 Requirements

### BACK — Backend Infrastructure

- [ ] **BACK-01**: FastAPI app with `CORSMiddleware` configured from `ALLOWED_ORIGINS` env var (Vercel domain)
- [ ] **BACK-02**: `GET /health` endpoint returns 200 + timestamp for uptime monitoring
- [ ] **BACK-03**: `GET /api/models` returns hardcoded list of available openai-hk.com model IDs and display names (sourced from env var or config)
- [ ] **BACK-04**: `POST /api/generate/text` accepts JSON body `{topic, num_questions, model}` and returns a `QuizResponse`
- [ ] **BACK-05**: `POST /api/generate/file` accepts multipart form `{files: list[UploadFile], extra_context?, num_questions, model}` — designed for one or more files, v1 UI sends one
- [ ] **BACK-06**: IP-based rate limiting via `slowapi` — 3 requests/IP/hour — applied to both generate endpoints before any public URL is shared

### AI — LLM Integration

- [ ] **AI-01**: Prompt builder assembles `system_prompt` (schema instructions + constraints) and `user_content` (topic or extracted text) into `messages[]`
- [ ] **AI-02**: LLM called via `AsyncOpenAI(base_url="https://www.openai-hk.com/v1")` with `response_format="json_object"`, `temperature=0.7`, `max_tokens=4096`, `timeout=55s`
- [ ] **AI-03**: Response validated with Pydantic `QuizSchema` — each question has `question_type`, `question`, `options: list[str] | None`, `correct_indices: list[int] | None`, `explanation: str`
- [ ] **AI-04**: v1 system prompt requests only `"multiple_choice"` question type — schema is designed for future types (`true_false`, `multiple_select`, `short_answer`) without code changes
- [ ] **AI-05**: Auto-retry once with corrective re-prompt on `JSONDecodeError` or Pydantic validation failure; return HTTP 502 on second failure

### UPLOAD — File Processing

- [ ] **UPLOAD-01**: PDF text extracted via `pypdf` — `PdfReader(io.BytesIO(content))`, text joined page-by-page
- [ ] **UPLOAD-02**: Plain text files (`.txt`) decoded as UTF-8
- [ ] **UPLOAD-03**: Extracted text from all uploaded files concatenated with `\n\n---\n\n` separator before passing to prompt builder
- [ ] **UPLOAD-04**: Optional `extra_context` text field (from `/generate/file` multipart) prepended to extracted document text — enables combining typed notes with an uploaded document
- [ ] **UPLOAD-05**: Scanned PDF detection — if extracted word count < 50 for a multi-page PDF, reject with user-facing message: "This PDF appears to be scanned. Please upload a text-based PDF."
- [ ] **UPLOAD-06**: Combined extracted text truncated to 12,000 chars with user notification when truncation occurs
- [ ] **UPLOAD-07**: File upload size capped at 10MB per file; files with more than 30 pages rejected with clear error

### FE — Frontend

- [ ] **FE-01**: Tabbed input panel — "Topic" tab (text prompt field) and "Upload" tab (single-file picker for v1; backend already supports multiple)
- [ ] **FE-02**: Configuration panel — question count selector (5 / 10 / 15 / 20) and model selector dropdown (populated from `GET /api/models`)
- [ ] **FE-03**: `useReducer` state machine with five explicit states: `idle → generating → reviewing → exporting → idle`
- [ ] **FE-04**: Stepped loading feedback shown immediately on submit — "Uploading… → Extracting text… → Generating questions…"
- [ ] **FE-05**: Quiz review screen — numbered questions, options labeled A/B/C/D, correct answer(s) highlighted, explanation shown below each question
- [ ] **FE-06**: Empty state with 3 example topic prompts to reduce blank-page paralysis on first visit
- [ ] **FE-07**: Graceful error display for: API failure, scanned PDF, empty prompt, rate limit hit, file too large

### EXP — Export

- [ ] **EXP-01**: "Copy to clipboard" button — formats quiz as readable plain text (question + options + answer key)
- [ ] **EXP-02**: "Download JSON" button — downloads the `questions[]` array as a `.json` file

### DEPLOY — Deployment & Operations

- [ ] **DEPLOY-01**: Backend deployed and publicly reachable on Railway; `$PORT` used for uvicorn binding
- [ ] **DEPLOY-02**: Frontend deployed and publicly reachable on Vercel; `VITE_API_BASE_URL` env var points to Railway backend URL
- [ ] **DEPLOY-03**: `OPENAI_API_KEY`, `ALLOWED_ORIGINS`, and `AVAILABLE_MODELS` set as Railway environment variables — no secrets in code

---

## v2 Requirements (deferred)

- Multi-file picker UI (single file in v1; backend already supports list)
- `multiple_select` and `true_false` question types (schema already supports them)
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
| `correct_indices: list[int]` not `correct_index: int` | Single-answer MCQ uses `[0]`; multi-select uses `[0,2]` — no schema migration when multi-select is added |
| `question_type` discriminator field in schema | Enables true_false, multiple_select, short_answer in v1.1 with only a prompt change + new renderer |
| `files: list[UploadFile]` on backend (v1 UI sends one) | Adding multi-file is a pure frontend change; backend already handles the list |
| `extra_context` optional field on `/generate/file` | Allows combining typed notes + uploaded document without a new endpoint |
| Two generate endpoints not one | Browsers cannot mix JSON and multipart in one request; two endpoints is correct design |
| Hardcoded model list in env var | Live `/v1/models` fetch risks key exposure and adds a startup dependency |
| Rate limiting before public URL | anonymous app = no billing firewall; 3 req/IP/hour added in Phase 2 |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 | Phase 1: Backend Scaffold | Pending |
| BACK-02 | Phase 1: Backend Scaffold | Pending |
| BACK-03 | Phase 1: Backend Scaffold | Pending |
| BACK-04 | Phase 2: AI Generation Pipeline | Pending |
| BACK-05 | Phase 4: File Upload Backend | Pending |
| BACK-06 | Phase 2: AI Generation Pipeline | Pending |
| AI-01 | Phase 2: AI Generation Pipeline | Pending |
| AI-02 | Phase 2: AI Generation Pipeline | Pending |
| AI-03 | Phase 2: AI Generation Pipeline | Pending |
| AI-04 | Phase 2: AI Generation Pipeline | Pending |
| AI-05 | Phase 2: AI Generation Pipeline | Pending |
| UPLOAD-01 | Phase 4: File Upload Backend | Pending |
| UPLOAD-02 | Phase 4: File Upload Backend | Pending |
| UPLOAD-03 | Phase 4: File Upload Backend | Pending |
| UPLOAD-04 | Phase 4: File Upload Backend | Pending |
| UPLOAD-05 | Phase 4: File Upload Backend | Pending |
| UPLOAD-06 | Phase 4: File Upload Backend | Pending |
| UPLOAD-07 | Phase 4: File Upload Backend | Pending |
| FE-01 | Phase 5: File Upload Frontend | Pending |
| FE-02 | Phase 7: Model Selection UI | Pending |
| FE-03 | Phase 3: React Frontend — Topic Flow | Pending |
| FE-04 | Phase 3: React Frontend — Topic Flow | Pending |
| FE-05 | Phase 3: React Frontend — Topic Flow | Pending |
| FE-06 | Phase 3: React Frontend — Topic Flow | Pending |
| FE-07 | Phase 3: React Frontend — Topic Flow | Pending |
| EXP-01 | Phase 6: Export | Pending |
| EXP-02 | Phase 6: Export | Pending |
| DEPLOY-01 | Phase 1: Backend Scaffold | Pending |
| DEPLOY-02 | Phase 3: React Frontend — Topic Flow | Pending |
| DEPLOY-03 | Phase 1: Backend Scaffold | Pending |
