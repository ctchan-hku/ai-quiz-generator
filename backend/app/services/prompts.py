"""LLM system and follow-up prompt text."""

from app.models.mcq_constraints import (
    MCQ_CORRECT_INDICES_MIN_COUNT,
    MCQ_EXPLANATION_SOFT_MAX_CHARS,
    MCQ_OPTION_COUNT_DEFAULT,
    MCQ_OPTION_COUNT_MAX,
    MCQ_OPTION_COUNT_MIN,
)

MULTIPLE_CHOICE_CONSTRAINTS = f"""Each multiple-choice question object must satisfy all rules below.

Required fields:
- question_type: must be "multiple_choice".
- question: stem text only (no numbering), and it must clearly state what is being asked.
- options: {MCQ_OPTION_COUNT_MIN} to {MCQ_OPTION_COUNT_MAX} unique strings.
  Use {MCQ_OPTION_COUNT_DEFAULT} options by default unless the topic needs a different count.
- correct_indices: list of zero-based positions for the correct option(s).
  - At least {MCQ_CORRECT_INDICES_MIN_COUNT} value.
  - Values must be distinct integers in [0, len(options)-1].
  - Position mapping: 0=A (first), 1=B (second), 2=C (third), 3=D (fourth).
  - If explanation says the answer is C, correct_indices must be [2].
- explanation: one JSON string (never an array), with step-by-step deduction from stem to answer.
  - Use numbered or labeled steps in that single string.
  - Keep it specific, not vague.
  - Prefer <= ~{MCQ_EXPLANATION_SOFT_MAX_CHARS} characters unless the stem needs more.
"""

MCQ_CHAIN_OF_THOUGHT = """First generate a question stem.
Then deduct and calculate the correct and valid answer based on the question.
State the full deduction steps in the explanation.
Then create other options to distract the user, and append them with the correct answer in an options list.
Set correct_indices only to the row(s) containing the truthful answer(s)."""

REWRITE_HINT = f"""
When reviewing your output, verify the following:
1. Fact-check: Is each identified correct answer objectively true?
2. Stem: Is the question stem unambiguous, unnumbered, and aligned with the marked correct option(s)?
3. Distractors: Are incorrect options plausible relative to the stem (same topic/vocabulary), not absurd?
4. Explanation: Does it use numbered or clearly labeled deduction steps—not a vague single sentence?
5. Length: Is each explanation roughly within ~{MCQ_EXPLANATION_SOFT_MAX_CHARS} characters unless more is clearly needed?
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
