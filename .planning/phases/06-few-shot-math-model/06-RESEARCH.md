# Phase 6 — Research notes

**Date:** 2026-04-27  
**Scope:** Few-shot injection + `gpt-4.1` catalog (no regeneration).

## Findings

1. **`build_messages` / `generate_quiz`** (`backend/app/services/llm.py`) — Single system string today. Few-shot block appends after `SYSTEM_PROMPT_HEADER` + `MultipleChoiceQuestion.system_prompt` per **06-CONTEXT.md D-6-06**.

2. **`parse_with_retry`** (`backend/app/services/parser.py`) — Reuses `messages` for the corrective call; initial `messages` must already include the few-shot system content (**AI-FS-03**).

3. **`GenerateTextRequest`** (`backend/app/routers/generate.py`) — Add optional `few_shot_examples`; validate via shared normalizer (max 3 non-empty after trim, each ≤ 2000 chars).

4. **Models** — `_FALLBACK_MODELS` in `backend/app/config.py`; `GET /api/models` reads `settings.available_models` — no router change expected.

5. **Frontend** — `generateQuiz` in `frontend/src/lib/api.ts` takes positional args; extend to accept optional examples or pass a single request object — planner chose: extend `QuizFormConfig` + `generateQuiz` to thread optional `few_shot_examples` (omit when empty). `useQuizMachine` mutation passes full `QuizFormConfig`.

6. **UI** — **D-6-09** (updated): dynamic list with Add / Remove; no default rows; cap 3.

## Risks

- **Provider model id:** `gpt-4.1` may differ on openai-hk.com — ops adjusts `AVAILABLE_MODELS` only (**D-6-02**).

## References

- `.planning/phases/06-few-shot-math-model/06-CONTEXT.md`
- `.planning/REQUIREMENTS.md` — MOD-01/02, AI-FS-*, FE-FS-*, DEPLOY-04
