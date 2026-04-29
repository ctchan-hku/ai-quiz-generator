"""LLM system and follow-up prompt text."""

from app.models.mcq_constraints import (
    MCQ_CORRECT_INDICES_MIN_COUNT,
    MCQ_OPTION_COUNT_DEFAULT,
    MCQ_OPTION_COUNT_MAX,
    MCQ_OPTION_COUNT_MIN,
)

MULTIPLE_CHOICE_CONSTRAINTS = f"""Each multiple-choice question object must contain:
- question_type: "multiple_choice"
- question: The stem (no numbering). It must unambiguously state exactly what is being asked.
- options: A list of between {MCQ_OPTION_COUNT_MIN} and {MCQ_OPTION_COUNT_MAX} unique strings (default to {MCQ_OPTION_COUNT_DEFAULT} options when the topic does not dictate otherwise).
- correct_indices: A list of indices of the correct option(s)—at least {MCQ_CORRECT_INDICES_MIN_COUNT} correct index(es), each distinct, from 0 through len(options)-1.
- explanation: Must be one JSON string (never an array of strings). Put numbered or labeled steps (e.g. step 1, step 2) in that single string—use newlines between steps. Stepped deduction from stem to the correct answer(s); not a vague one-liner. Prefer ≤ ~1000 characters unless the stem requires more.
"""

MCQ_CHAIN_OF_THOUGHT = """First generate a question stem.
Then deduct and calculate the correct and valid answer based on the question.
State the full deduction steps in the explanation.
Then create other options to distract the user, and append them with the correct answer in an options list.
Set correct_indices only to the row(s) containing the truthful answer(s)."""

REWRITE_HINT = """
When reviewing your output, verify the following:
1. Fact-check: Is each identified correct answer objectively true?
2. Stem: Is the question stem unambiguous, unnumbered, and aligned with the marked correct option(s)?
3. Distractors: Are incorrect options plausible relative to the stem (same topic/vocabulary), not absurd?
4. Explanation: Does it use numbered or clearly labeled deduction steps—not a vague single sentence?
5. Length: Is each explanation roughly within ~1000 characters unless more is clearly needed?
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
