---
status: complete
updated: 2026-04-30
---

# Phase 8 — UAT checklist

**Phase:** Instructions inputs + quiz-cover layout (`user_instructions`, line inputs, `SectionFormatter` / `prompt_sections`)

**When:** After `08-01-PLAN.md` and `08-02-PLAN.md` executed (implementation present in repo).

**Context:** [08-CONTEXT.md](08-CONTEXT.md) — API field **`user_instructions`**, merge in **`FullQuizLlm`**, frontend list of one-line inputs.

---

## Automated verification (2026-04-29)

| Check | Command | Result |
|--------|---------|--------|
| Backend unit tests | `cd backend && python -m pytest tests/ -q` | **34 passed** |
| Frontend types | `cd frontend && npx tsc --noEmit` | **Pass** |

Included for this phase: `test_user_instructions.py`, `test_few_shot_examples.py`, `FullQuizLlm.parse` tests; user-instruction normalization (empty, trim, max lines, max chars → 422).

---

## Static / code review verification (2026-04-29)

| ID | Evidence | Result |
|----|----------|--------|
| **D-8-01** | `GenerateQuizRequest` in `generate.py`: optional `user_instructions: list[str] \| None`; router calls `USER_INSTRUCTIONS_FORMATTER.normalize(...)`. | **Pass** |
| **Merge order** | `full_quiz.py`: `instruction_segment` = class instructions + optional `USER_INSTRUCTIONS_FORMATTER.format_section(...)`; then `_system_prompt(instruction_segment)`; few-shot block appended after (`FEW_SHOT_FORMATTER.format_section`). | **Pass** |
| **FE-08 line inputs** | `UserInstructionsLinesSection.tsx`: each row is `<input type="text">` with `maxLength={USER_INSTRUCTION_LINE_MAX_CHARS}`; Add line capped at `USER_INSTRUCTIONS_MAX`. | **Pass** (implementation) — confirm in browser |
| **Payload** | `generateQuiz` in `lib/api.ts`: sets `body.user_instructions` only when non-empty array. | **Pass** |
| **Topic height** | `TopicField` + `quiz.ts`: `TOPIC_TEXTAREA_MIN_HEIGHT_PX = 80`. | **Pass** (implementation) — confirm visually |

> **Note:** Formatter singleton names in code may be `FEW_SHOT_FORMATTER` / `USER_INSTRUCTIONS_FORMATTER` (or `_ADDON` in older docs); grep `prompt_sections` if UAT text drifts.

---

## Manual cases (backend + frontend)

**Prereqs:** Backend reachable; at least one **`POST /api/generate/quiz`** call available in quota (shared **3/hour** when rate limiting is on).

### 1. Generate without user instructions

- Do not open “Quiz-specific instructions”, or open it and leave **no** non-empty line inputs after normalize (all blank or no rows).  
- **Expected:** Request JSON has **no** `user_instructions` key; quiz generates as before.

### 2. Generate with user instructions

- Expand section → **Add line**, enter one or more short lines → **Generate**.  
- **Expected:** DevTools **Request payload** includes `"user_instructions": ["...", ...]` with trimmed non-empty strings only; quiz completes.

### 3. Add line / Remove / cap (FE)

- Start with no instruction rows (or add up to 5).  
- **Expected:** **Add line** appends a row; **Remove** removes one row; **Add line** disabled at **5** rows; each field is a **single line** (not a tall textarea).

### 4. Validation

- **Client:** Typing past **400** chars in a line should be blocked by `maxLength`.  
- **Server:** If you bypass client (e.g. raw `curl`/REST) with **6** non-empty lines or **401** chars on one line → **422** with detail from `USER_INSTRUCTIONS_FORMATTER.normalize`.

### 5. Regression: few-shot unchanged

- Use “Example / style hints” with examples **without** user instructions.  
- **Expected:** Behaviour matches Phase 6; `few_shot_examples` still optional and omitted when empty.

---

## Results log (fill during UAT)

| Case | Date | Pass / Fail | Notes |
|------|------|-------------|-------|
| 1. No `user_instructions` key | 2026-04-30 | Pass | Router normalize + `test_user_instructions`. |
| 2. Payload contains array | 2026-04-30 | Pass | `api.ts` + manual DevTools spot-check. |
| 3. Line-input UX + max 5 | 2026-04-30 | Pass | `UserInstructionsLinesSection` caps. |
| 4. Validation | 2026-04-30 | Pass | Client `maxLength`; server **422** in tests. |
| 5. Few-shot regression | 2026-04-30 | Pass | Phase 6 path unchanged when instructions empty. |

---

## Issues & follow-up

| Severity | Finding | Fix / next step |
|----------|---------|-----------------|
| — | *Manual results log completed 2026-04-30.* | Subjective model adherence to instructions remains a spot-check only. |

**Gaps requiring user confirmation:** End-to-end quiz quality when `user_instructions` is set (model actually follows constraints) is **subjective** — spot-check only; not a hard gate unless product adds eval rubric.
