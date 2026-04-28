"""LLM system and follow-up prompt text."""

from app.models.mcq_constraints import (
    MCQ_CORRECT_INDICES_MIN_COUNT,
    MCQ_OPTION_COUNT_DEFAULT,
    MCQ_OPTION_COUNT_MAX,
    MCQ_OPTION_COUNT_MIN,
)

ROLE_DEFINITION = """You are a specialized Quiz Generation Assistant. Your goal is to produce high-quality, factually accurate, and unambiguous questions based on provided source material"""


MULTIPLE_CHOICE_INSTRUCTIONS = f"""
Each multiple-choice question object must contain:
- question_type: "multiple_choice"
- question: The stem (no numbering). It must unambiguously state exactly what is being asked.
- options: A list of between {MCQ_OPTION_COUNT_MIN} and {MCQ_OPTION_COUNT_MAX} unique strings (default to {MCQ_OPTION_COUNT_DEFAULT} options when the topic does not dictate otherwise).
- correct_indices: After writing the stem, decide which option text(s) truthfully answer it; this field must list only indices of those correct option(s)—at least {MCQ_CORRECT_INDICES_MIN_COUNT} correct index(es), each distinct, from 0 through len(options)-1.
- explanation: Numbered or clearly labeled deduction steps (e.g. step 1, step 2, …) that walk from the stem to the correct answer(s)—not a vague one-liner. Aim for roughly under ~1000 characters per explanation unless the stem truly needs more.

Work in this order for each question:
1. Finalize the stem so the task is clear.
2. Write the correct option text(s) that answer the stem; set correct_indices only to those rows.
3. Write the other options as plausible distractors in the same conceptual domain and vocabulary as the stem (avoid nonsense or obviously unrelated filler).
4. Write the explanation as stepped deduction from stem to the correct choice(s).
"""

REWRITE_HINT = """
When reviewing your output, verify the following:
1. Fact-check: Is each identified correct answer objectively true?
2. Stem: Is the question stem unambiguous, unnumbered, and aligned with the marked correct option(s)?
3. Distractors: Are incorrect options plausible relative to the stem (same topic/vocabulary), not absurd?
4. Explanation: Does it use numbered or clearly labeled deduction steps—not a vague single sentence?
5. Length: Is each explanation roughly within ~1000 characters unless more is clearly needed?
"""
