# Roadmap — AI Quiz Generator MVP

**Version:** v1 (MVP)
**Last updated:** 2026-04-22 (Phase 1: debug chat-completion)
**Granularity:** Standard (5-8 phases)
**Coverage:** 31/31 requirements mapped ✓

---

## Phases

- [ ] **Phase 1: Backend Scaffold** — FastAPI app, CORS, /health, /api/models, optional `POST /api/debug/chat-completion`, Railway deploy
- [ ] **Phase 2: AI Generation Pipeline** — /api/generate/text, prompt builder, LLM client, Pydantic schema, rate limiting
- [ ] **Phase 3: React Frontend — Topic Flow** — QuizForm, useReducer state machine, QuizDisplay, error states, Vercel deploy
- [ ] **Phase 4: File Upload Backend** — /api/generate/file, pypdf extraction, scanned PDF guard, truncation, limits
- [ ] **Phase 5: File Upload Frontend** — Tabbed input, file picker, multipart submit
- [ ] **Phase 6: Export** — JSON download, clipboard copy, ExportPanel
- [ ] **Phase 7: Model Selection UI** — Dropdown from /api/models wired to all generate requests

---

## Phase Details

### Phase 1: Backend Scaffold
**Goal**: A deployable FastAPI backend is publicly reachable on Railway with working health and model endpoints, plus an optional gated LLM smoke route for manual testing.
**Depends on**: Nothing
**Requirements**: BACK-01, BACK-02, BACK-03, BACK-07, DEPLOY-01, DEPLOY-03
**Success Criteria** (what must be TRUE):
  1. `GET /health` at the Railway URL returns HTTP 200 with a timestamp
  2. `GET /api/models` returns the configured model list as JSON
  3. CORS middleware accepts requests from the allowed origin (Vercel domain or `*` during dev)
  4. Railway environment variables (`OPENAI_API_KEY`, `ALLOWED_ORIGINS`, `AVAILABLE_MODELS`) are set and loaded
  5. When `ENABLE_DEBUG_CHAT_COMPLETION=true`, `POST /api/debug/chat-completion` with a valid `model` returns a short real assistant reply; when the flag is false, the route returns 404 or is absent
**Plans**:
  - Scaffold FastAPI app with `CORSMiddleware`, `/health`, and `/api/models` routes
  - Add `pydantic-settings` config module loading env vars from Railway (include `ENABLE_DEBUG_CHAT_COMPLETION`, optional `OPENAI_BASE_URL` if not hardcoded)
  - Add `openai` dependency; implement `POST /api/debug/chat-completion` behind `ENABLE_DEBUG_CHAT_COMPLETION` with allowlisted `model`, capped `max_tokens`, and shared `base_url`/API key settings
  - Write `requirements.txt` / `pyproject.toml` and `nixpacks.toml` (or `Procfile`) for Railway
  - Deploy backend to Railway; set environment variables in Railway dashboard
  - Smoke-test CORS from browser console against the live Railway URL; optionally curl debug route with flag on in staging only

### Phase 2: AI Generation Pipeline
**Goal**: The API can generate a valid multiple-choice quiz from a text topic, with automatic error recovery and rate limiting.
**Depends on**: Phase 1
**Requirements**: BACK-04, BACK-06, AI-01, AI-02, AI-03, AI-04, AI-05
**Success Criteria** (what must be TRUE):
  1. `POST /api/generate/text` with `{topic, num_questions, model}` returns a `QuizResponse` with well-formed questions
  2. Each v1 question validates as `MultipleChoiceQuestion`: `question_type: "multiple_choice"`, `question`, `explanation`, exactly four `options`, `correct_indices` with exactly one index in range
  3. A `JSONDecodeError` or Pydantic validation failure triggers one automatic corrective retry; second failure returns HTTP 502
  4. More than 3 requests from the same IP within one hour returns HTTP 429
**Plans**:
  - Build `models/schemas.py` — `QuestionBase` (`question`, `explanation`); `OptionsQuestion` (`options`, `correct_indices`); `MultipleChoiceQuestion`, `TrueFalseQuestion`, `MultiSelectQuestion`, `ShortAnswerQuestion` (`expected_answer`); `QuizQuestion` as discriminated union on `question_type`; `QuizSchema(questions: list[QuizQuestion])`; per-class validators; v1 LLM output only `multiple_choice`
  - Build `services/llm.py` — prompt builder assembling `system_prompt` + `user_content` into `messages[]`, `AsyncOpenAI(base_url="openai-hk.com/v1")` client with `json_object` mode, `temperature=0.7`, `max_tokens=4096`, `timeout=55s`
  - Build response parser — `json.loads` + Pydantic validation with one auto-retry on corrective re-prompt; strip markdown fences before parsing
  - Build `routers/generate.py` — `POST /api/generate/text` endpoint; integrate `slowapi` rate limiter (3 req/IP/hour)
  - Integration test: `curl` the live Railway endpoint with a sample topic and verify response schema

### Phase 3: React Frontend — Topic Flow
**Goal**: Users can type a topic in the browser, generate a quiz, and review the questions and answers on screen.
**Depends on**: Phase 2
**Requirements**: FE-03, FE-04, FE-05, FE-06, FE-07, DEPLOY-02
**Success Criteria** (what must be TRUE):
  1. User types a topic, clicks Generate, and sees a quiz displayed on screen
  2. Stepped loading states appear immediately on submit — "Generating questions..." — without waiting for the first API byte
  3. Quiz review shows numbered questions, A/B/C/D options, highlighted correct answer(s), and explanation below each question
  4. Empty state shows 3 example prompts; all error cases (API failure, rate limit, empty prompt) display a readable message
**Plans**:
  - Scaffold Vite + React 19 + TypeScript + Tailwind v4 + shadcn/ui project; configure `VITE_API_BASE_URL`
  - Build `useQuizMachine` hook with `useReducer` state machine: `idle → generating → reviewing → exporting → idle`; form config (`topic`, `numQuestions`, `model`) survives state transitions
  - Build `QuizForm` component — topic textarea, question count selector (5/10/15/20), submit button with immediate disable-on-click; stepped loading text during `generating` state
  - Build `QuizDisplay` component — numbered questions, A/B/C/D labeled options, highlighted correct answer(s), explanation text, empty state with 3 example prompts, error state card; TypeScript types mirror backend `QuizQuestion` discriminated union (v1 branch handles only `multiple_choice`)
  - Deploy frontend to Vercel; set `VITE_API_BASE_URL` to Railway backend URL; verify end-to-end topic → quiz flow
**UI hint**: yes

### Phase 4: File Upload Backend
**Goal**: The backend accepts uploaded PDF and text files, extracts their text, and generates a quiz from the document content.
**Depends on**: Phase 2
**Requirements**: BACK-05, UPLOAD-01, UPLOAD-02, UPLOAD-03, UPLOAD-04, UPLOAD-05, UPLOAD-06, UPLOAD-07
**Success Criteria** (what must be TRUE):
  1. `POST /api/generate/file` with a `.pdf` or `.txt` file returns a valid `QuizResponse`
  2. A scanned PDF (< 50 extracted words on a multi-page document) returns HTTP 422 with message "This PDF appears to be scanned. Please upload a text-based PDF."
  3. Combined extracted text exceeding 12,000 chars is truncated; the response includes a `truncated: true` flag
  4. Files over 10MB or PDFs with more than 30 pages are rejected with a clear error message before any extraction
**Plans**:
  - Build `services/extraction.py` — `pypdf` PDF extraction (`PdfReader(io.BytesIO(content))`, joined page-by-page); UTF-8 decode for `.txt` files
  - Add multi-file text concatenation with `\n\n---\n\n` separator; prepend optional `extra_context` field before document text
  - Add scanned PDF guard (word count < 50 on multi-page → HTTP 422) and 12,000-char truncation with `truncated` flag in response
  - Build `POST /api/generate/file` endpoint — `files: list[UploadFile]`, `extra_context: str | None`, `num_questions`, `model`; enforce 10MB per-file cap and 30-page PDF rejection
  - Test with a real text PDF, a scanned PDF, a large PDF (> 30 pages), and a `.txt` file on the live Railway endpoint

### Phase 5: File Upload Frontend
**Goal**: Users can upload a PDF or text file through the browser to generate a quiz from its content.
**Depends on**: Phase 3, Phase 4
**Requirements**: FE-01
**Success Criteria** (what must be TRUE):
  1. Tabbed input panel shows "Topic" and "Upload" tabs; switching tabs preserves question count and model selection
  2. File picker accepts `.pdf` and `.txt` files; selecting a file displays its filename and enables the Generate button
  3. Submitting with a file sends a correctly structured multipart request to `/api/generate/file`
  4. File-specific errors (scanned PDF, file too large, truncation notice) display as readable messages in the UI
**Plans**:
  - Refactor `QuizForm` from single-mode to tabbed layout using shadcn Tabs — "Topic" tab (existing) and "Upload" tab
  - Build file picker — click-to-browse + drag-and-drop; accept `.pdf,.txt`; display selected filename; validate file size client-side before submit
  - Wire multipart `FormData` submission via Axios to `/api/generate/file`; include `num_questions`, `model`, and optional `extra_context`
  - Add upload progress state and stepped loading text for file flow ("Uploading… → Extracting text… → Generating questions…"); map file-specific API error codes to readable messages
**UI hint**: yes

### Phase 6: Export
**Goal**: Users can export their generated quiz as a downloadable JSON file or copy it as formatted plain text to their clipboard.
**Depends on**: Phase 3
**Requirements**: EXP-01, EXP-02
**Success Criteria** (what must be TRUE):
  1. "Copy to clipboard" produces readable plain text with numbered questions, A/B/C/D options, and an answer key
  2. "Download JSON" saves the `questions[]` array as a `.json` file named after the topic or timestamp
  3. Both export actions are accessible from the quiz review screen after generation completes
  4. Clipboard copy works in Chrome, Firefox, and Safari; download works without server round-trip
**Plans**:
  - Build `ExportPanel` component with "Copy to clipboard" and "Download JSON" buttons using shadcn Button
  - Implement clipboard copy — format quiz as plain text (`Q1: … A) … B) … Answer: B`) using `navigator.clipboard.writeText`
  - Implement JSON download — `Blob` + `URL.createObjectURL` triggered programmatically; filename `quiz-{topic}-{date}.json`
  - Integrate `ExportPanel` into `QuizDisplay`; wire to `exporting` state in `useQuizMachine`; confirm copy with brief success toast
**UI hint**: yes

### Phase 7: Model Selection UI
**Goal**: Users can choose which AI model to use for generation from a dropdown populated live from the backend.
**Depends on**: Phase 3
**Requirements**: FE-02
**Success Criteria** (what must be TRUE):
  1. Model selector dropdown lists model display names fetched from `GET /api/models` on page load
  2. Question count selector (5/10/15/20) is present alongside the model selector in the configuration panel
  3. Selected model is sent in all generate requests (both topic and file modes)
  4. Dropdown defaults to the first model in the list; selection persists across quiz regenerations in the same session
**Plans**:
  - Fetch `GET /api/models` with TanStack Query `useQuery` on app mount; cache model list for the session
  - Build model selector dropdown in the configuration panel using shadcn Select; show model display names; default to first model
  - Wire selected model into both `useMutation` payloads (text generate + file generate) via `useQuizMachine` form config state
  - Handle models endpoint loading and error states — skeleton during load, fallback message on fetch failure
**UI hint**: yes

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Backend Scaffold | 0/6 | Not started | - |
| 2. AI Generation Pipeline | 0/5 | Not started | - |
| 3. React Frontend — Topic Flow | 0/5 | Not started | - |
| 4. File Upload Backend | 0/5 | Not started | - |
| 5. File Upload Frontend | 0/4 | Not started | - |
| 6. Export | 0/4 | Not started | - |
| 7. Model Selection UI | 0/4 | Not started | - |

---

## Coverage Map

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 | Phase 1 | Pending |
| BACK-02 | Phase 1 | Pending |
| BACK-03 | Phase 1 | Pending |
| BACK-07 | Phase 1 | Pending |
| BACK-04 | Phase 2 | Pending |
| BACK-05 | Phase 4 | Pending |
| BACK-06 | Phase 2 | Pending |
| AI-01 | Phase 2 | Pending |
| AI-02 | Phase 2 | Pending |
| AI-03 | Phase 2 | Pending |
| AI-04 | Phase 2 | Pending |
| AI-05 | Phase 2 | Pending |
| UPLOAD-01 | Phase 4 | Pending |
| UPLOAD-02 | Phase 4 | Pending |
| UPLOAD-03 | Phase 4 | Pending |
| UPLOAD-04 | Phase 4 | Pending |
| UPLOAD-05 | Phase 4 | Pending |
| UPLOAD-06 | Phase 4 | Pending |
| UPLOAD-07 | Phase 4 | Pending |
| FE-01 | Phase 5 | Pending |
| FE-02 | Phase 7 | Pending |
| FE-03 | Phase 3 | Pending |
| FE-04 | Phase 3 | Pending |
| FE-05 | Phase 3 | Pending |
| FE-06 | Phase 3 | Pending |
| FE-07 | Phase 3 | Pending |
| EXP-01 | Phase 6 | Pending |
| EXP-02 | Phase 6 | Pending |
| DEPLOY-01 | Phase 1 | Pending |
| DEPLOY-02 | Phase 3 | Pending |
| DEPLOY-03 | Phase 1 | Pending |
