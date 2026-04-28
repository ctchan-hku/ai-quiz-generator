# Phase 9 — RESEARCH (locked for planning)

**Phase:** 09 — Reasoning-first MCQs, stepped explanations, distractors, shuffle, topic/example balance  
**Date:** 2026-04-29

## Decisions

### 1. Orchestration: single LLM call (Phase 9 scope)

- **Choice:** Strengthen **one** `json_object` response per quiz / per single-MCQ so the model is instructed to derive the stem, lock correct answer(s), add plausible distractors, and write a **stepped** explanation — without a second API round-trip in the first ship.
- **Rationale:** Matches existing `parse_with_retry`, minimal latency and cost, no new dependencies (no LangChain).
- **Escape hatch:** If UAT shows weak distractors, a follow-up plan can add an optional second pass (distractors-only) using the same `AsyncOpenAI` client pattern.

### 2. Option order: server-side shuffle only

- **Choice:** After `MultipleChoiceQuestion` passes validation (including `truncate_excess_options`), apply a **cryptographic shuffle** of option rows and **remap** `correct_indices`.
- **Rationale:** Removes systematic “answer A” bias without relying on prompt compliance; unit-testable; same behavior for full-quiz and refine.
- **Placement:** Post-parse in `FullQuizLlm.parse` / `SingleMcqLlm.parse` (or small helper used by both), not in another `model_validator`, so tests and API contracts stay obvious.

### 3. Explanation length vs `max_tokens`

- **Choice:** **Prompt-first** contract: ask for numbered deduction steps with a **target cap** (e.g. ≤ ~800–1200 characters per explanation) before adding a hard Pydantic `max_length` that could break legacy clients.
- **Rationale:** Shared `MAX_COMPLETION_TOKENS` (4096 today) already bounds the whole quiz JSON; per-field schema limits are a follow-up if abuse appears.

### 4. Topic vs few-shot balance

- **Choice:** Keep examples in the **system** message; **reword the user message** so `{topic}` is labeled as scope/coverage only and, when `few_shot_examples` is non-empty, add an explicit line that **example lines take precedence for tone, difficulty, and stem format**.
- **Rationale:** Current user line over-weights “about: {topic}`” (`full_quiz.py`). No router change beyond string content unless we add a dedicated subsection in `FEW_SHOT_FORMATTER` (optional polish in same plan).

### 5. Prompt structure for “correctness first, then distractors”

- **Choice:** Extend `MULTIPLE_CHOICE_INSTRUCTIONS` (and `REWRITE_HINT` if needed) with a **fixed internal order**: (a) finalize stem; (b) determine correct option text(s); (c) write other options as plausible errors; (d) write `explanation` as numbered steps justifying (b).
- **Rationale:** One JSON object; model sees explicit workflow without multi-step infrastructure.

## References (code)

- `backend/app/services/prompts.py`
- `backend/app/services/llm/full_quiz.py`, `single_mcq.py`
- `backend/app/helpers/options.py` (`truncate_options` — shuffle will live alongside or in same module)
- `backend/app/models/schemas.py`

## Out of scope (Phase 9)

- LangChain / LangGraph.
- RAG or external tool calls.
- Automated semantic verification of factual correctness (manual UAT + prompt only).
