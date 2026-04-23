# Phase 2: AI Generation Pipeline — Research

**Researched:** 2026-04-22
**Status:** RESEARCH COMPLETE

---

## Prompt Engineering Techniques (from promptingguide.ai)

### Applicable Techniques for Quiz Generation

**1. Few-Shot Prompting (highest impact)**

From the guide: "Few-shot prompting can be used as a technique to enable in-context learning where we provide demonstrations in the prompt to steer the model to better performance."

For structured JSON output, including 1–2 fully-formed example `MultipleChoiceQuestion` objects in the system prompt anchors the model to the exact schema shape. This is more reliable than schema-only instructions, especially for `correct_indices` (array vs scalar is a common failure mode).

Recommended: embed one worked example directly in the system prompt, before the rules list.

**2. Prompt Elements Structure (Instruction → Context → Input → Output Indicator)**

The guide defines four prompt elements: Instruction, Context, Input Data, Output Indicator.

Applied to quiz generation:
- **Instruction**: "You are a quiz generation assistant. Output ONLY a raw JSON array."
- **Context**: Schema rules + one worked example (few-shot)
- **Input Data**: User message — "Generate {N} questions about: {topic}"
- **Output Indicator**: The `response_format={"type": "json_object"}` API parameter reinforces this

**3. Specificity and "Say What To Do" (not what not to do)**

From the guide: "Avoid saying what not to do but say what to do instead."

Bad pattern: "Do not include explanations or markdown."
Good pattern: "Respond with raw JSON only. Your entire response must be a valid JSON array."

The current architecture doc's system prompt mixes both. The planned prompt should lead with the positive specification.

**4. Separator-Based Formatting (###)**

The guide recommends clear separators between instruction and context. Applied to the corrective re-prompt on retry: use `### JSON ERROR` or `### INVALID FORMAT` as a separator before injecting the original response + correction request.

**5. Zero-Shot with `json_object` Mode**

For gpt-4o and gpt-4o-mini, `response_format={"type": "json_object"}` provides zero-shot JSON enforcement at the API level. This ensures syntactically valid JSON but NOT schema correctness — Pydantic validation is still required. The approach is: API-level JSON guarantee + application-level schema validation + one corrective retry.

---

## Validation Architecture

### Dimension 8 — Nyquist Sampling Strategy

The core validation risk for this phase is the LLM response parser failing silently or retrying incorrectly. Key sampling points:

1. **Schema instantiation** — unit test each Pydantic model variant directly
2. **Discriminated union dispatch** — test that `question_type` field routes correctly to each variant
3. **Parser happy path** — valid JSON → `QuizSchema` with no retry
4. **Parser retry path** — malformed JSON → corrective re-prompt → valid response → `QuizSchema`
5. **Parser double-failure path** — two consecutive failures → HTTP 502
6. **Rate limiter** — 4th request within 1 hour from same IP → HTTP 429 with correct message (D-01)
7. **Endpoint integration** — live Railway curl test with real topic → valid `QuizResponse`

---

## Technical Research Findings

### Pydantic Discriminated Union — Correct Pattern

```python
from typing import Annotated, ClassVar, Union
from pydantic import BaseModel, Field, field_validator

class BaseQuestion(BaseModel):
    question_type: str
    question: str
    explanation: str

class OptionsQuestion(BaseQuestion):
    options: list[str]
    correct_indices: list[int]

class SingleAnswerQuestion(OptionsQuestion):
    expected_options_count: ClassVar[int]

    @field_validator("options")
    @classmethod
    def exact_options_count(cls, v: list[str]) -> list[str]:
        if len(v) != cls.expected_options_count:
            raise ValueError(f"{cls.__name__} requires exactly {cls.expected_options_count} options, got {len(v)}")
        return v

    @field_validator("correct_indices")
    @classmethod
    def single_correct_index(cls, v: list[int]) -> list[int]:
        if len(v) != 1:
            raise ValueError(f"{cls.__name__} correct_indices must have exactly 1 element, got {len(v)}")
        return v

class MultipleChoiceQuestion(SingleAnswerQuestion):
    question_type: Literal["multiple_choice"]
    expected_options_count: ClassVar[int] = 4

# Discriminated union using Annotated + Field(discriminator=...)
QuizQuestion = Annotated[
    Union[MultipleChoiceQuestion, TrueFalseQuestion, MultiSelectQuestion, ShortAnswerQuestion],
    Field(discriminator="question_type"),
]

class QuizSchema(BaseModel):
    questions: list[QuizQuestion]
```

**Why discriminated union over manual dispatch:** Pydantic resolves the correct variant in O(1) using the `question_type` literal — no branching logic needed in application code (PRCP-05 from clean-code rules).

### LLM Client — Dependency Injection Pattern

Per clean-code rule PRCP-06 (dependency injection), the `AsyncOpenAI` client should NOT be instantiated inside the route handler. Inject it via FastAPI's `Depends`:

```python
# services/llm.py
from openai import AsyncOpenAI
from app.config import settings

def get_llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=55,
    )
```

This keeps the router thin and the service testable.

### System Prompt — Few-Shot Design

Apply the promptingguide.ai few-shot technique: include one complete example in the system prompt.

```
You are a quiz generation assistant. Your ONLY output is a raw JSON array of questions.
Do not include markdown, explanation, or text outside the JSON array.

Each question must have EXACTLY this shape:
{
  "question_type": "multiple_choice",
  "question": "<question text>",
  "options": ["<A>", "<B>", "<C>", "<D>"],
  "correct_indices": [<single integer 0-3>],
  "explanation": "<one sentence>"
}

Rules:
- Exactly 4 options
- correct_indices contains exactly one integer in range [0, 3]
- Questions must be factually grounded

Example (1-shot):
[
  {
    "question_type": "multiple_choice",
    "question": "What is the capital of France?",
    "options": ["Berlin", "Madrid", "Paris", "Rome"],
    "correct_indices": [2],
    "explanation": "Paris has been the capital of France since the 12th century."
  }
]
```

**Why 1-shot (not 0-shot):** The `correct_indices` field (list of int) is non-obvious and frequently confused with a scalar `correct_index`. One worked example eliminates this failure mode without bloating the prompt.

### Auto-Retry — Corrective Re-Prompt

On `JSONDecodeError` or Pydantic `ValidationError`, send a corrective follow-up using the failed response + correction request:

```python
# services/parser.py (or inline in llm.py)
CORRECTIVE_SYSTEM = (
    "The JSON you returned was invalid. "
    "Return ONLY the corrected JSON array. No explanation."
)

async def parse_with_retry(raw: str, client: AsyncOpenAI, model: str, messages: list) -> QuizSchema:
    try:
        return _parse(raw)
    except (json.JSONDecodeError, ValidationError):
        corrective_messages = messages + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": f"That response was invalid JSON or failed schema validation. Correct it and return only the JSON array."},
        ]
        retry_response = await client.chat.completions.create(
            model=model,
            messages=corrective_messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4096,
        )
        retry_raw = retry_response.choices[0].message.content
        try:
            return _parse(retry_raw)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise HTTPException(status_code=502, detail="LLM returned invalid quiz data after retry") from exc
```

**Separator technique from promptingguide.ai:** The corrective message clearly labels what failed ("That response was invalid JSON or failed schema validation") — specific, positive instruction on what to return.

### Rate Limiting — slowapi Integration

`slowapi` wraps `limits` and integrates with FastAPI via middleware + `Depends`:

```python
# main.py additions
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

```python
# routers/generate.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/generate/text")
@limiter.limit("3/hour")
async def generate_text(request: Request, ...):
    ...
```

**D-01 custom message:** Override the `_rate_limit_exceeded_handler` to return a JSON body with:
```json
{"detail": "You've hit the limit of 3 quizzes per hour. Please wait before trying again."}
```

The default slowapi handler returns plain text. A custom handler ensures consistent JSON across all error responses.

### File Layout

```
backend/app/
├── models/
│   └── schemas.py          # BaseQuestion, OptionsQuestion, all variants, QuizSchema, QuizResponse
├── services/
│   ├── llm.py              # AsyncOpenAI client factory, prompt builder, generate() function
│   └── parser.py           # _parse(), parse_with_retry()
└── routers/
    └── generate.py         # POST /api/generate/text, slowapi decorator, request/response wiring
```

`main.py` additions: limiter setup, exception handler, `app.include_router(generate.router)`.

### Requirements Mapping

| Requirement | Implementation |
|-------------|---------------|
| BACK-04 | `POST /api/generate/text` in `routers/generate.py` |
| BACK-06 | slowapi `@limiter.limit("3/hour")` + custom 429 message (D-01) |
| AI-01 | `build_prompt(topic, num_questions)` → `messages[]` in `services/llm.py` |
| AI-02 | `AsyncOpenAI(base_url=...)` with `json_object`, `temperature=0.7`, `max_tokens=4096`, `timeout=55` |
| AI-03 | Pydantic discriminated union in `models/schemas.py` |
| AI-04 | System prompt with `question_type: "multiple_choice"` constraints + 1-shot example |
| AI-05 | `parse_with_retry()` in `services/parser.py` |

---

## Risks and Landmines

1. **`correct_indices` confusion** — LLM may return scalar (`0`) instead of array (`[0]`). The few-shot example and explicit "array with exactly one element" in rules mitigates this. The Pydantic validator catches it regardless.
2. **Markdown fence leakage** — even with `json_object` mode, some models prepend ` ```json `. Strip markdown fences before `json.loads`.
3. **slowapi import name** — `from slowapi import Limiter` and `from slowapi.util import get_remote_address`. The `_rate_limit_exceeded_handler` is in `slowapi` namespace, not `slowapi.util`.
4. **Custom 429 handler** — `_rate_limit_exceeded_handler` must be registered AFTER `app.state.limiter = limiter`, and before route registration.
5. **`response_format` model support** — `json_object` mode is supported by gpt-4o and gpt-4o-mini. If a future model is added that doesn't support it, the call will raise an error. Log a warning and fall back to non-json_object mode if needed (post-MVP).

---

## ## RESEARCH COMPLETE
