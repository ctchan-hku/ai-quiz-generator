"""LLM prompt copy, MCQ rule text, and full-quiz list-section formatters."""

from app.modules.generation.config.mc_question import (
    MC_QUESTION_CORRECT_INDICES_MIN_COUNT,
    MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS,
    MC_QUESTION_OPTION_COUNT_DEFAULT,
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.services.section_formatter import SectionFormatter

MULTIPLE_CHOICE_CONSTRAINTS = f"""Each multiple-choice question object must satisfy all rules below.

Required fields:
- question_type: must be "multiple_choice".
- question: stem text only (no numbering), and it must clearly state what is being asked.
- options: {MC_QUESTION_OPTION_COUNT_MIN} to {MC_QUESTION_OPTION_COUNT_MAX} unique strings.
  Use {MC_QUESTION_OPTION_COUNT_DEFAULT} options by default unless the topic needs a different count.
- correct_indices: list of zero-based positions for the correct option(s).
  - At least {MC_QUESTION_CORRECT_INDICES_MIN_COUNT} value.
  - Values must be distinct integers in [0, len(options)-1].
  - Position mapping: 0=A (first), 1=B (second), 2=C (third), 3=D (fourth).
  - If explanation says the answer is C, correct_indices must be [2].
  - Consistency rule: explanation result, correct option content, and correct_indices must all point to the same answer.
- explanation: one JSON string (never an array), with step-by-step deduction from stem to answer.
  - Use numbered or labeled steps in that single string.
  - Keep it specific, not vague.
  - Prefer <= ~{MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS} characters unless the stem needs more.
"""

MC_QUESTION_CHAIN_OF_THOUGHT = """Follow this order:
1. Generate the question stem.
2. Deduce the correct result from the stem.
3. Write deduction steps and final result in explanation.
4. Create one option that matches the final result exactly.
5. Create distractor options to fill the required count (plausible near-miss or similar alternatives).
6. Set correct_indices to the zero-based position(s) of the true option(s).
7. Final check: explanation result, correct option value, and correct_indices must be consistent."""

REWRITE_HINT = f"""
When reviewing your output, verify the following:
1. Fact-check: Is each identified correct answer objectively true?
2. Stem: Is the question stem unambiguous, unnumbered, and aligned with the marked correct option(s)?
3. Distractors: Are incorrect options plausible relative to the stem (same topic/vocabulary), not absurd?
4. Explanation: Does it use numbered or clearly labeled deduction steps—not a vague single sentence?
5. Length: Is each explanation roughly within ~{MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS} characters unless more is clearly needed?
"""

QUIZ_SOURCE_PRIORITY_GUIDANCE = """Source priority (highest to lowest):
1) Examples (scenario style, detail level, reasoning pattern)
2) User instructions and constraints
3) Topic

Topic is a domain label only. It defines the subject area and terminology, but does NOT override the scenario patterns from examples.

Generation policy:
- First, extract scenario/content patterns from examples (what kinds of situations are asked, what reasoning is expected).
- Then generate new questions that follow those patterns within the topic domain.
- If topic conflicts with examples, keep the example pattern and adapt entities/terms to the topic.
- Do not produce generic topic trivia when examples imply scenario-based questions."""

FEW_SHOT_MAX_ITEMS = 3
FEW_SHOT_MAX_LINE_CHARS = 2000

FEW_SHOT_FORMATTER: SectionFormatter = SectionFormatter(
    FEW_SHOT_MAX_ITEMS,
    FEW_SHOT_MAX_LINE_CHARS,
    (
        "Reference examples below demonstrate the expected question structure, difficulty level, "
        "and formatting style. Analyze their patterns—scope, phrasing, answer format—and apply "
        "these conventions to new questions. Generate original content that matches this quality bar.\n"
    ),
)

USER_INSTRUCTION_MAX_ITEMS = 5
USER_INSTRUCTION_MAX_LINE_CHARS = 400

USER_INSTRUCTIONS_FORMATTER: SectionFormatter = SectionFormatter(
    USER_INSTRUCTION_MAX_ITEMS,
    USER_INSTRUCTION_MAX_LINE_CHARS,
    (
        "User-specific requirements—apply these constraints and preferences when generating questions. "
        "These override defaults but should complement the reference examples' style:\n"
    ),
)
