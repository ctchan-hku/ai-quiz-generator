# Phase 9 — CONTEXT (draft)

**Status:** Research + plan ready — see [09-RESEARCH.md](09-RESEARCH.md) and [09-01-PLAN.md](09-01-PLAN.md). Lock remaining product nuance with `/gsd-spec-phase 9` if you need REQ IDs in `REQUIREMENTS.md`.

## Goal

Raise **quiz quality** so that: (1) stems and keyed answers are **truth-consistent**; (2) explanations show **explicit reasoning / deduction steps**; (3) wrong options are **credibly distracting** relative to the stem; (4) answer positions are **not biased** toward a slot (e.g. index 0); (5) when users supply **topic + examples**, generation **balances** topic as broad direction against examples as **structure / domain / difficulty** anchors (examples must not be ignored).

## Requirements (draft IDs — assign in REQUIREMENTS.md)

### Correctness first

- The model must treat the question stem as ground truth for what is being asked; the correct option(s) must agree with that stem **before** wording distractors.
- Optional eval rubric later: spot-check / automated hints that `correct_indices` align with stem (phase research: single-pass JSON vs explicit chain-of-thought internally).

### Explanation = full deduction steps

- Replace or extend **“concise rationale”** in prompts so `explanation` captures **ordered reasoning steps** (not one vague sentence).
- SCHEMA / prompt contract: clarify min expectations (numbered steps vs paragraphs) without breaking JSON size limits.

### Distractors after the answer line

- Prompt workflow: derive **verified** correct answer(s), then invent **plausible distractors** that misuse same vocabulary / partial logic (not random unrelated facts).
- May combine with correctness instructions above.

### Shuffle options server-side

- After validation (and after any truncation if applicable), **shuffle** option rows so the correct answer does not systematically appear first.
- Implement **deterministic remap** of `correct_indices` after shuffle (`secrets`/crypto RNG acceptable).
- Extend same behavior to **`SingleMcqLlm`** / refine flows if MCQ parsing allows post-process.

### Topic vs few-shot examples (balance)

- Today the **user message** emphasizes “questions **about**: {topic}”. Examples live in the **system prompt** appendix — model may overweight topic breadth.
- Product intent: **topic** = scope / hint / coverage direction; **examples** = primary signals for tone, difficulty, stem shape, domain.
- Prompt + message layout changes (order, labels, explicit “prefer example patterns when examples exist”), possibly lighter topic phrasing.

## Depends on

- Phase 8 (instructions + quiz layout) — complete.

## Open questions (research before PLAN)

1. Shuffle only in backend vs also instruct model to randomize (prefer single server-side shuffle for consistency).
2. Explanation length vs token limits (`max_tokens` / truncation policy).
3. Single LLM call with structured internal sections vs cheap second pass for distractors-only.

## References

- Prompts: `backend/app/services/prompts.py` (`MULTIPLE_CHOICE_INSTRUCTIONS`), `REWRITE_HINT`.
- Full-quiz messages: `backend/app/services/llm/full_quiz.py` — user message line `Generate … about: {topic}`, few-shot append order.
- Schema: `MultipleChoiceQuestion` — `correct_indices`, `options`, `explanation`.
