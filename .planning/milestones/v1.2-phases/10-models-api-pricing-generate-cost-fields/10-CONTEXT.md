# Phase 10: Models API pricing + generate cost fields — Context

**Gathered:** 2026-04-30  
**Status:** Ready for execution  
**Source:** Milestone v1.2 roadmap + REQUIREMENTS (plan-phase without separate discuss-phase)

## Phase boundary

Deliver backend-only changes: **`GET /api/models`** exposes **price metadata** per configured model (USD per million input/output tokens, compatible with [`backend/scripts/fetch_poe_ai_models.py`](../../../backend/scripts/fetch_poe_ai_models.py) conventions). **`POST /api/generate/quiz`** and **`POST /api/generate/question`** success responses include **`cost_usd`** (estimated from OpenAI-style **`usage`** × those rates). Phase **11** consumes these fields in the React app.

## Implementation decisions

- **`AVAILABLE_MODELS`** remains the allowlist: each element is at least `id` + `label`; add optional nested **`price`**: `{ "input": number | null, "output": number | null }` where values are **USD per 1M tokens** (same semantics as `fetch_poe_ai_models.py` output). Models without prices return **`price`: null** or omit `price`; README documents behavior for sorting/display (Phase 11).
- **Cost estimate:** After each successful completion (including parse retry if a second completion runs), sum **`prompt_tokens`** and **`completion_tokens`** from the OpenAI SDK **`usage`** object(s). `cost_usd = (prompt/1e6)*price.input + (completion/1e6)*price.output` using the requested **model id**'s rates; missing usage or missing price component → treat that component as **0** and document (tests assert deterministic behavior).
- **`QuizResponse`** gains **`cost_usd: float`** (non-negative). **`POST /api/generate/question`** switches **`response_model`** to a **wrapper** that includes **`question: MultipleChoiceQuestion`** and **`cost_usd: float`** so the MCQ schema stays pure — Phase 11 updates TS types accordingly (breaking JSON shape for that endpoint only).
- **No secrets** in responses beyond aggregate usage-derived cost; no user PII.

## Canonical references

- [`.planning/REQUIREMENTS.md`](../../REQUIREMENTS.md) — MOD-03, MOD-04, API-COST-01, API-COST-02  
- [`.planning/ROADMAP.md`](../../ROADMAP.md) — Phase 10 success criteria  
- [`backend/app/routers/models.py`](../../../backend/app/routers/models.py) — current `/api/models`  
- [`backend/app/routers/generate.py`](../../../backend/app/routers/generate.py) — generate routes  
- [`backend/app/services/llm/openai/client.py`](../../../backend/app/services/llm/openai/client.py) — `complete_chat`  
- [`backend/app/services/parser.py`](../../../backend/app/services/parser.py) — `parse_llm_with_retry`  
- [`backend/app/models/generate_responses.py`](../../../backend/app/models/generate_responses.py) — `QuizResponse`, `QuestionGenerateResponse`; [`quiz.py`](../../../backend/app/models/quiz.py) — parsed `Quiz` for `FullQuizLlm`

## Deferred

- Streaming token UI, billing caps, persistence — later milestones.

---

*Phase: 10-models-api-pricing-generate-cost-fields*
