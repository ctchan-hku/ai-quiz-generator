# Architecture Patterns: AI Quiz Generator

**Domain:** AI-powered quiz generation web app (FastAPI + React)
**Researched:** 2026-04-22
**Confidence:** HIGH — patterns are well-established; specifics verified against FastAPI docs and OpenAI SDK patterns

**Planning source of truth:** `.planning/REQUIREMENTS.md` (§ Question schema) defines the **discriminated union** for quiz questions (`QuestionBase` → `OptionsQuestion` variants + `ShortAnswerQuestion`). Examples below use the v1 `multiple_choice` shape; flat `correct_index`-only models are obsolete.

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────┐
│               Vercel (Frontend)                  │
│                                                  │
│  React (Vite)                                    │
│  ┌──────────────────────────────────────────┐   │
│  │  QuizForm (topic / file + config)        │   │
│  │  → QuizDisplay (review + export)         │   │
│  │  → ExportPanel (JSON / clipboard)        │   │
│  └──────────────────────────────────────────┘   │
│       │ fetch (multipart or JSON)                │
└───────┼─────────────────────────────────────────┘
        │  HTTPS (CORS)
┌───────▼─────────────────────────────────────────┐
│               Railway (Backend)                  │
│                                                  │
│  FastAPI                                         │
│  ┌──────────────────────────────────────────┐   │
│  │  POST /api/generate/text                 │   │
│  │  POST /api/generate/file                 │   │
│  │  GET  /api/models                        │   │
│  │  GET  /health                            │   │
│  └──────────────────────────────────────────┘   │
│       │                                          │
│  ┌────▼──────────────────────────────────────┐  │
│  │  Extraction Layer                         │  │
│  │  text: pass-through / truncate            │  │
│  │  PDF:  pypdf → extract_text()             │  │
│  └────┬──────────────────────────────────────┘  │
│       │                                          │
│  ┌────▼──────────────────────────────────────┐  │
│  │  Prompt Builder                           │  │
│  │  system_prompt + user_content → messages  │  │
│  └────┬──────────────────────────────────────┘  │
│       │                                          │
│  ┌────▼──────────────────────────────────────┐  │
│  │  OpenAI SDK (base_url = openai-hk.com)    │  │
│  │  client.chat.completions.create(...)      │  │
│  └────┬──────────────────────────────────────┘  │
│       │ raw LLM text                             │
│  ┌────▼──────────────────────────────────────┐  │
│  │  Response Parser                          │  │
│  │  extract JSON → validate schema           │  │
│  └────┬──────────────────────────────────────┘  │
│       │ QuizResponse (Pydantic)                  │
└───────┼─────────────────────────────────────────┘
        │  JSON
┌───────▼─────────────────────────────────────────┐
│  openai-hk.com (OpenAI-compatible LLM API)       │
└──────────────────────────────────────────────────┘
```

---

## Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| QuizForm | Collect topic/file + config (model, count) | → Backend via fetch |
| QuizDisplay | Render generated questions, highlight answers | ← State store |
| ExportPanel | JSON download, clipboard copy | ← State store |
| FastAPI router | Route HTTP → handler, validate request | → Extraction, Prompt Builder |
| Extraction Layer | File bytes → plain text string | ← Router, → Prompt Builder |
| Prompt Builder | Assemble system + user messages | ← Router + Extraction, → LLM client |
| LLM Client | Call openai-hk.com API | ← Prompt Builder, → Response Parser |
| Response Parser | Raw LLM text → validated Pydantic model | ← LLM Client, → Router |

---

## API Endpoint Design

### `POST /api/generate/text`

**Payload** (JSON body):
```json
{
  "topic": "The French Revolution",
  "num_questions": 10,
  "model": "gpt-4o-mini"
}
```

**Response** (JSON) — v1 items are all `multiple_choice` union members:
```json
{
  "questions": [
    {
      "question_type": "multiple_choice",
      "question": "What year did the French Revolution begin?",
      "options": ["1776", "1789", "1804", "1815"],
      "correct_indices": [1],
      "explanation": "The Revolution began in 1789 with the Estates-General."
    }
  ],
  "model_used": "gpt-4o-mini",
  "source": "topic"
}
```

**Validation:**
- `topic`: 1–2000 chars, required
- `num_questions`: int, 1–50, default 10
- `model`: must be in allowed list

---

### `POST /api/generate/file`

**Payload** (multipart/form-data):
```
file: <binary>          # .txt or .pdf, max 10 MB
num_questions: 10
model: gpt-4o-mini
```

**Response**: same schema as `/generate/text`, `source: "file"`

**Rationale for two endpoints over one:** Multipart and JSON are mutually exclusive content types in browsers. Mixing them into one endpoint forces awkward form handling. Two clean endpoints is the right split.

---

### `GET /api/models`

**Response:**
```json
{
  "models": [
    { "id": "gpt-4o-mini", "label": "GPT-4o Mini (fast, cheap)" },
    { "id": "gpt-4o",      "label": "GPT-4o (smart, slower)"  }
  ],
  "default": "gpt-4o-mini"
}
```

This list is configured server-side (env var or hardcoded list). The frontend never fetches the live model list from openai-hk.com directly — that would expose the API key.

---

### `POST /api/debug/chat-completion` (Phase 1, optional)

**Purpose:** Manual smoke test — one real chat completion via the same client config as production (`OPENAI_API_KEY`, `base_url`).

**Mounted only when** `ENABLE_DEBUG_CHAT_COMPLETION=true` (default off). Otherwise omit the router or return 404.

**Request (JSON):**
```json
{
  "model": "gpt-4o-mini",
  "message": "Reply with one word: ok"
}
```

`model` must match an id from the configured allowlist (`AVAILABLE_MODELS`). Cap `max_tokens` low (e.g. ≤64). Do not use `response_format: json_object` here unless you want structured smoke output.

**Response:** JSON with assistant message text and `model_used`. **Disable on public production** unless explicitly needed; pairs with Phase 2 rate limiting when the app is fully public.

---

### `GET /health`

```json
{ "status": "ok", "version": "0.1.0" }
```

Used by Railway health checks and frontend startup probing.

---

## Prompt Engineering

### System Prompt (fixed, not user-controlled)

```
You are a quiz generation assistant. Your ONLY job is to output a JSON array of
multiple-choice questions. Do not include any explanation, markdown, or commentary
— respond with raw JSON only.

Each question in the array must have EXACTLY this shape (v1 — multiple_choice only):
{
  "question_type": "multiple_choice",
  "question": "<question text>",
  "options": ["<A>", "<B>", "<C>", "<D>"],
  "correct_indices": [<single index 0-3>],
  "explanation": "<one sentence why the answer is correct>"
}

Rules:
- Exactly 4 options per question
- correct_indices is an array with exactly one element, 0–3
- Questions must be unambiguous and factually grounded
- Do not number the questions
- Do not include any text outside the JSON array
```

### User Message (dynamic, varies by source)

**Topic mode:**
```
Generate {num_questions} multiple-choice questions about: {topic}
```

**File mode (extracted text injected):**
```
The following is content extracted from an uploaded document. Generate
{num_questions} multiple-choice questions strictly based on this content.
Do not invent facts not present in the document.

---
{extracted_text}
---
```

### Why `response_format: { "type": "json_object" }` (if model supports it)

Use `response_format={"type": "json_object"}` in the API call when the model supports it (gpt-4o, gpt-4o-mini do). This guarantees the response is valid JSON — but does NOT guarantee schema correctness. Always validate with Pydantic regardless.

For models that don't support `json_object` mode, rely on the system prompt alone and parse defensively.

### LLM Call Parameters

```python
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message},
    ],
    response_format={"type": "json_object"},  # when supported
    temperature=0.7,    # some creativity but consistent
    max_tokens=4096,    # ~10 questions comfortably fit
    timeout=60,         # Railway timeout headroom
)
```

---

## File Content Extraction and LLM Feeding

### Text Files (`.txt`, `.md`)
```python
text = file_bytes.decode("utf-8", errors="replace")
```
No special library needed. Errors replaced rather than raised.

### PDF Files (`.pdf`)
Use **pypdf** (pure Python, no system deps, Railway-friendly):
```python
from pypdf import PdfReader
import io

reader = PdfReader(io.BytesIO(file_bytes))
text = "\n".join(page.extract_text() or "" for page in reader.pages)
```

**pypdf** is preferred over `pdfminer.six` (heavier), `pymupdf` (C bindings, Railway complications), or `pdfplumber` (adds dependency on `pdfminer.six`). Pure Python + Railway = pypdf.

### Chunking vs Truncation

**Decision: Truncation only for MVP.** Chunking (split → generate per chunk → merge) is correct but complex. For MVP:

```python
MAX_CHARS = 12_000  # ~3000 tokens; leaves room for prompt + response

def truncate_text(text: str, max_chars: int = MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... document truncated for length ...]"
```

12,000 chars ≈ 3,000 tokens. With a 128K context window (gpt-4o), headroom is generous — but smaller/cheaper models may have tighter limits. Flag this in PITFALLS.

**Chunking** (post-MVP): Split text into overlapping chunks, generate N questions per chunk, deduplicate. Add this only if users complain that long documents produce shallow questions.

### Accepted MIME Types

```python
ALLOWED_TYPES = {"text/plain", "application/pdf"}
ALLOWED_EXTENSIONS = {".txt", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
```

Validate both MIME type (from browser) and extension (from filename). Don't trust either alone.

---

## Frontend State Machine

```
idle
  │  user submits form
  ▼
generating
  │  fetch resolves (success)        fetch rejects / error response
  ▼                                   ▼
reviewing  ◄──── regenerate ─────────error
  │
  │  user clicks export
  ▼
exporting  (modal/panel opens, no network call)
  │
  │  user clicks "New Quiz"
  ▼
idle
```

### State Shape (React — `useReducer`)

```typescript
type QuizState =
  | { status: "idle" }
  | { status: "generating" }
  | { status: "reviewing"; quiz: Quiz; source: "topic" | "file" }
  | { status: "error"; message: string }
  | { status: "exporting"; quiz: Quiz };

type Quiz = {
  questions: QuizQuestion[];
  model_used: string;
  source: "topic" | "file";
};

// Mirror backend discriminated union; v1 UI only renders multiple_choice
type QuizQuestion =
  | {
      question_type: "multiple_choice";
      question: string;
      explanation: string;
      options: [string, string, string, string];
      correct_indices: [number];
    }
  | {
      question_type: "true_false";
      question: string;
      explanation: string;
      options: [string, string];
      correct_indices: [number];
    }
  | {
      question_type: "multiple_select";
      question: string;
      explanation: string;
      options: string[];
      correct_indices: number[];
    }
  | {
      question_type: "short_answer";
      question: string;
      explanation: string;
      expected_answer: string;
    };
```

**Use `useReducer` not `useState`** — the state machine has enough transitions that `useState` becomes tangled. `useReducer` with explicit actions (SUBMIT, SUCCESS, ERROR, EXPORT, RESET) makes transitions auditable.

### Form Config State (separate, always editable)

```typescript
type FormConfig = {
  mode: "topic" | "file";
  topic: string;
  file: File | null;
  numQuestions: number;
  model: string;
};
```

Keep form config in `useState` separate from quiz machine state. The form persists across regenerations; the quiz state resets.

---

## Data Flow

### Topic Generation

```
1. User fills form (topic, numQuestions, model)
2. Frontend: POST /api/generate/text  { topic, num_questions, model }
3. Backend: validates input → builds prompt → calls LLM
4. LLM returns: raw JSON string (or json_object mode enforces JSON)
5. Backend: parses JSON → validates Pydantic → returns QuizResponse
6. Frontend: transitions idle→generating→reviewing, renders questions
```

### File Generation

```
1. User selects file + configures numQuestions + model
2. Frontend: POST /api/generate/file  multipart { file, num_questions, model }
3. Backend: validates size/type → reads bytes → extracts text (pdf or txt)
4. Backend: truncates if needed → builds prompt with extracted_text injected
5. LLM returns: raw JSON string
6. Backend: parses → validates → returns QuizResponse
7. Frontend: transitions idle→generating→reviewing
```

### Export

```
1. User in "reviewing" state clicks Export
2. Frontend transitions reviewing→exporting (no network call)
3. ExportPanel renders:
   a. Download JSON:  blob URL download of JSON.stringify(quiz)
   b. Copy to clipboard:  navigator.clipboard.writeText(formattedText)
4. User dismisses panel → back to reviewing
```

---

## CORS Configuration

Backend must allow Vercel frontend origin. Configure FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://your-app.vercel.app",     # production
    "http://localhost:5173",            # local dev (Vite default)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,            # no cookies, no auth
)
```

Use `allow_origins=["*"]` ONLY during local development, never in production. Vercel provides a stable deployment URL to whitelist.

---

## Error Handling Patterns

### Backend Error Taxonomy

```python
class QuizGenerationError(Exception):
    """Base for all generation errors."""

class FileExtractionError(QuizGenerationError):
    status_code = 422
    detail = "Could not extract text from the uploaded file."

class LLMTimeoutError(QuizGenerationError):
    status_code = 504
    detail = "The AI model took too long to respond. Try again."

class LLMMalformedOutputError(QuizGenerationError):
    status_code = 502
    detail = "The AI model returned an unexpected response. Try again."

class LLMRefusalError(QuizGenerationError):
    status_code = 422
    detail = "The AI model declined to generate questions for this content."
```

FastAPI exception handler maps these to HTTP responses with consistent `{ "detail": "..." }` shape.

### LLM Response Validation

Implement `QuizSchema` with `questions: list[QuizQuestion]` where `QuizQuestion` is a **Pydantic discriminated union** on `question_type` (see `.planning/REQUIREMENTS.md`). Outline:

```python
import json
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Annotated, Literal, Union

class QuestionBase(BaseModel):
    question: str
    explanation: str

class OptionsQuestion(QuestionBase):
    options: list[str]
    correct_indices: list[int]

class MultipleChoiceQuestion(OptionsQuestion):
    question_type: Literal["multiple_choice"] = "multiple_choice"
    @model_validator(mode="after")
    def validate_mcq(self):
        if len(self.options) != 4 or len(self.correct_indices) != 1:
            raise ValueError("MCQ requires 4 options and exactly one correct index")
        # ... bounds checks ...
        return self

class TrueFalseQuestion(OptionsQuestion):
    question_type: Literal["true_false"] = "true_false"
    # validators: len(options)==2, len(correct_indices)==1

class MultiSelectQuestion(OptionsQuestion):
    question_type: Literal["multiple_select"] = "multiple_select"
    # validators: len(correct_indices) >= 2, etc.

class ShortAnswerQuestion(QuestionBase):
    question_type: Literal["short_answer"] = "short_answer"
    expected_answer: str

QuizQuestion = Annotated[
    Union[MultipleChoiceQuestion, TrueFalseQuestion, MultiSelectQuestion, ShortAnswerQuestion],
    Field(discriminator="question_type"),
]

class QuizSchema(BaseModel):
    questions: list[QuizQuestion]

def parse_llm_response(raw: str) -> QuizSchema:
    # strip fences, json.loads, normalize to {"questions": [...]}, return QuizSchema(**data)
    ...
```

Additional validations live on each variant class (option counts, index ranges, multi-select min count). Minimum 1 question in output; strip non-empty text on all string fields.

### Frontend Error Display

```typescript
// Map HTTP status to user-friendly messages
function toUserMessage(status: number, detail: string): string {
  if (status === 504) return "Generation timed out — try a shorter document or fewer questions.";
  if (status === 422) return detail;  // backend detail is already user-safe
  if (status === 502) return "The AI returned an unexpected response. Please try again.";
  return "Something went wrong. Please try again.";
}
```

Always show the error prominently with a "Try Again" button that resets state to `idle` while preserving form config.

### Timeout Strategy

```python
# Backend: asyncio timeout wrapping the LLM call
import asyncio

async def call_llm_with_timeout(messages, model, timeout=55):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(client.chat.completions.create, ...),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise LLMTimeoutError()
```

55 seconds leaves 5 seconds of headroom before Railway's default 60-second request timeout. Frontend shows a spinner with elapsed time after 10 seconds to reassure users.

---

## Edge Cases

| Scenario | Detection | Handling |
|----------|-----------|----------|
| PDF with no extractable text (scanned image) | `extracted_text.strip() == ""` | Return 422: "This PDF appears to be image-based and cannot be read." |
| LLM returns fewer questions than requested | Validate `len(questions) < requested` | Accept and return what was generated; frontend shows actual count |
| LLM wraps JSON in markdown fence | Check for triple-backtick prefix | Strip fences before JSON parse |
| File too large (>10 MB) | Content-Length header or read size | Return 413 before reading body |
| Unsupported file type | MIME + extension check | Return 422 with allowed types listed |
| LLM refusal (content policy) | Response is a message, not JSON | JSON parse fails → LLMMalformedOutputError |
| Network timeout at Railway | asyncio timeout | LLMTimeoutError → 504 |
| model not in allowed list | Pydantic validator on model field | 422 validation error |
| openai-hk.com API key invalid/exhausted | openai.AuthenticationError | Return 503: "AI service unavailable" |

---

## Pydantic Request Models

```python
from pydantic import BaseModel, Field, validator

ALLOWED_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

class TextGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=2000)
    num_questions: int = Field(10, ge=1, le=50)
    model: str = Field("gpt-4o-mini")

    @validator("model")
    def validate_model(cls, v):
        if v not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of {ALLOWED_MODELS}")
        return v
```

File endpoint uses `Form(...)` parameters + `UploadFile` — Pydantic models don't directly apply to multipart. Validate manually in the handler.

---

## Build Order (Phase Implications)

Build in this order to unblock frontend work and avoid integration surprises:

**Phase 1 — Backend scaffold + health + CORS**
- FastAPI app, CORS middleware, `/health`, `/api/models`
- Deployable to Railway immediately; frontend can probe

**Phase 2 — Topic generation endpoint**
- `POST /api/generate/text`, prompt builder, LLM client, response parser
- Validates the entire LLM pipeline before file complexity

**Phase 3 — React frontend, topic flow**
- QuizForm (topic mode only), state machine, QuizDisplay
- Wire to Phase 2 endpoint; full e2e happy path working

**Phase 4 — Model selection UI** *(v1 roadmap; shipped with Phase 3 UI)*
- Model dropdown populated from `/api/models` (TanStack Query); native `<select>` in `QuizForm`
- Question count **0–10** with ± controls — matches `GenerateTextRequest` (`ge=0`, `le=10`), not fixed 5/10/15/20

**Phase 5 — Export** *(v1 roadmap)*
- JSON download, clipboard copy, ExportPanel
- Pure frontend; no backend changes; logically follows review (and Phase 4 config work in the plan)

**Deferred (v2) — File upload backend + frontend**
- `POST /api/generate/file`, pypdf extraction, file picker, multipart — see `REQUIREMENTS.md` v2

**Rationale:** v1 ships topic → quiz → review → export with model selection. Upload is deferred so the MVP stays a smaller surface. Each phase still aims for a working, deployable increment.

---

## Project Structure

```
/                          # repo root
├── backend/
│   ├── main.py            # FastAPI app, CORS, routers
│   ├── routers/
│   │   └── generate.py    # /api/generate/text + /api/generate/file
│   ├── services/
│   │   ├── llm.py         # LLM client, prompt builder, parser
│   │   └── extraction.py  # PDF + text extraction
│   ├── models/
│   │   └── schemas.py     # Pydantic request/response models
│   ├── config.py          # env vars (OPENAI_API_KEY, OPENAI_BASE_URL, etc.)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── QuizForm.tsx
│   │   │   ├── QuizDisplay.tsx
│   │   │   └── ExportPanel.tsx
│   │   ├── hooks/
│   │   │   └── useQuizMachine.ts   # useReducer state machine
│   │   ├── api/
│   │   │   └── client.ts           # typed fetch wrappers
│   │   └── types.ts                # shared TS types
│   ├── vite.config.ts
│   └── package.json
└── README.md
```

---

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `OPENAI_API_KEY` | Railway | API key for openai-hk.com |
| `OPENAI_BASE_URL` | Railway | `https://api.openai-hk.com/v1` |
| `ALLOWED_ORIGINS` | Railway | Comma-separated Vercel URLs |
| `VITE_API_URL` | Vercel | Railway backend URL |

The frontend uses only `VITE_API_URL`. All AI credentials stay server-side.

---

## Sources

- FastAPI CORS docs: https://fastapi.tiangolo.com/tutorial/cors/
- FastAPI file upload: https://fastapi.tiangolo.com/tutorial/request-files/
- OpenAI Python SDK (openai-hk.com is drop-in compatible): https://github.com/openai/openai-python
- pypdf (pure-Python PDF extraction): https://pypdf.readthedocs.io/
- OpenAI JSON mode: https://platform.openai.com/docs/guides/structured-outputs
- Confidence: HIGH — all patterns are standard FastAPI/OpenAI SDK idioms verified against official docs
