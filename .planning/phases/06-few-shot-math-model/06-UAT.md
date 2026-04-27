# Phase 6 — UAT checklist

**Phase:** Few-shot examples + gpt-4.1 catalog  
**When:** After `06-01-PLAN.md` and `06-02-PLAN.md` are executed.

**Implementation:** Wave 1 (API + `gpt-4.1` catalog) and Wave 2 (QuizForm add/remove few-shot rows, `generateQuiz(QuizFormConfig)`) are in place — run the checks below before closing the phase.

## Automated verification (2026-04-27)

- Backend: `cd backend && pytest` — 19 passed (includes `test_few_shot_examples` normalization).
- Frontend: `cd frontend && npx tsc --noEmit` — pass.

## Prerequisites

- Backend running (`uvicorn` or Railway); frontend dev with API proxy or remote env.
- `GET /api/models` includes **GPT-4.1 (math & reasoning)** when using default or updated `AVAILABLE_MODELS`.

## Cases

1. **Generate without examples**  
   - Do not open “Example / style hints” or leave no filled examples after normalize.  
   - **Expected:** `POST /api/generate/text` body has no `few_shot_examples` key; quiz generates as today.

2. **Generate with examples**  
   - Add one or more rows, enter non-empty style/sample text, submit.  
   - **Expected:** Request includes `few_shot_examples` array; quiz tone/structure differs in a plausible way vs (1) — note observation here for **AI-FS-04**.

3. **Add / Remove UX**  
   - Initial form: no example rows.  
   - Add up to 3 rows; Remove clears a row; Add disabled at 3 (or equivalent).  
   - **Expected:** Matches **D-6-09** in `06-CONTEXT.md`.

4. **Validation**  
   - Fourth non-empty example cannot be submitted (client); if forced via API, **422** (server).  
   - Overlong string (> 2000 chars) rejected client-side and/or **422** server-side.

## Notes (fill in during UAT)

| Run | Examples used? | Observation |
|-----|----------------|-------------|
| A | No | |
| B | Yes | |
