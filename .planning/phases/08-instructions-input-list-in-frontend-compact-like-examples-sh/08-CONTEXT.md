# Phase 8 — Context

**Gathered:** 2026-04-28  
**Status:** Ready for execution  
**Depends on:** Phase 7 complete

## Phase boundary

Deliver optional **short instruction lines** on the generate form (parallel UX to few-shot examples but **smaller per-row limits**), **shorten the topic “cover” textarea** visual height, and pass normalized instruction lines through **`POST /api/generate/quiz`** so **`FullQuizLlm`** merges them **with** `_question_class.instructions` inside the system prompt (not as a separate user-only block that bypasses field rules).

Out of scope: single-question refine (`/api/generate/question`), file upload, persistence of drafts beyond current form session.

## Implementation decisions (locked)

| ID | Decision |
|----|----------|
| D-8-01 | **API field name:** `user_instructions` — optional `list[str] \| null`, omission or `[]` means no extra instructions. |
| D-8-02 | **Caps (stricter than few-shot):** **max 5** lines × **400** characters per line after trim; constants live in `prompt_sections/user_instructions.py` (`USER_INSTRUCTIONS_MAX`, `USER_INSTRUCTION_LINE_MAX_CHARS`). |
| D-8-03 | **Normalization:** Implemented on `UserInstructions` / `FewShotExamples`, both exposing **`normalize`** via shared **`SectionFormatter`**; trim, drop empties, **422** on violation. |
| D-8-04 | **Prompt merge:** `USER_INSTRUCTIONS_ADDON.format_section` only formats the numbered user block (**no question-class text**). **`FullQuizLlm.build_messages`** concatenates `instructions` segment as `question_class.instructions` + newline + formatted user block when non-empty, then **`_system_prompt`**; few-shot appendix unchanged after that. |
| D-8-05 | **Few-shot ordering:** Keep order: merged instruction text → `outline()` content is already inside `_system_prompt` as middle segment — **verify** `_system_prompt` order: `ROLE` + `outline()` + `instructions`. User request: merge **with** `instructions`; implement by passing merged string as the **third** segment only (do not splice into `outline()`). |
| D-8-06 | **Frontend:** New `<details>` section “Quiz instructions” (or similar) mirroring `FewShotExamplesSection` with **smaller** `minHeight` per textarea and stricter `maxLength`; reduce `TOPIC_TEXTAREA_MIN_HEIGHT_PX` in `config/quiz.ts` (e.g. 120 → 72–80). |
| D-8-07 | **Types:** Extend `GenerateQuizRequest` / client types with optional `user_instructions`; thread through `QuizFormConfig` and `generateQuiz` (omit key when empty). |

## Canonical references

- `backend/app/services/llm/core/bases.py` — `_system_prompt`, `outline()`
- `backend/app/services/llm/full_quiz.py` — `build_messages`, `FullQuizLlm.__init__`
- `backend/app/routers/generate.py` — `GenerateQuizRequest`, `generate_quiz`
- `backend/app/services/prompt_sections/section_formatter.py` — **`SectionFormatter`** (`normalize` + `format_section`)
- `backend/app/services/prompt_sections/user_instructions.py` — user instruction lines
- `backend/app/services/prompt_sections/few_shot.py` — few-shot style examples (`FewShotExamples` + `FEW_SHOT_ADDON`)
- `frontend/src/components/QuizForm/FewShotExamplesSection.tsx` — row/add/remove pattern
- `frontend/src/config/quiz.ts` — shared limits

## Deferred

- i18n labels; analytics.
