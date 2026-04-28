# Phase 8 — Research

**Status:** Complete (orchestrator-authored)  
**Question:** How do we add instruction lines end-to-end without duplicating few-shot logic awkwardly?

## Findings

### Current flow

- **Router** `generate_quiz` builds `FullQuizLlm(topic, num_questions, few_shot_examples=examples)` — no instruction field today (`backend/app/routers/generate.py`).
- **FullQuizLlm** `build_messages()` calls `self._system_prompt(self._question_class.instructions)` then appends `format_few_shot_system_section` when few-shot present (`full_quiz.py`).
- **Base** `_system_prompt` concatenates `ROLE` + `outline()` + `instructions` string (`core/bases.py`).

### Recommended merge strategy

1. Add `instruction_lines: list[str] | None` to `FullQuizLlm.__init__`.
2. Add helper e.g. `merge_question_instructions(base: str, lines: list[str]) -> str` in `few_shot.py` (or `prompts.py`): append a short header + numbered lines after `base` when `lines` non-empty.
3. Pass `merge_question_instructions(MultipleChoiceQuestion.instructions, normalized_lines)` into `_system_prompt(...)`.
4. Keep few-shot block **after** full system string (unchanged relative order vs topic user message).

### Frontend pattern

Mirror `FewShotExamplesSection` with separate config constants `INSTRUCTION_MAX_ROWS`, `INSTRUCTION_LINE_MAX_CHARS`, smaller `minHeight` CSS, new details block below or above few-shot to avoid confusion.

### Risks

- **Token growth:** Many short lines still add tokens; caps (D-8-02) mitigate.
- **Duplicate user content:** If user pastes same content in topic and instructions; acceptable.

## Validation architecture

- **Unit:** `normalize_instruction_lines` (or equivalent) mirrors few-shot tests — empty, trim, count, length 422.
- **Integration:** Extend parser tests or add router test if project pattern allows — optional.
- **Frontend:** `tsc --noEmit`, manual network tab shows `instruction_lines` only when non-empty.
