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
- question: The stem (no numbering).
- options: A list of between {MCQ_OPTION_COUNT_MIN} and {MCQ_OPTION_COUNT_MAX} unique strings (default to {MCQ_OPTION_COUNT_DEFAULT} options when the topic does not dictate otherwise).
- correct_indices: A non-empty list of distinct integers, each from 0 through len(options)-1, selecting at least {MCQ_CORRECT_INDICES_MIN_COUNT} correct answer(s) (one or more indices as appropriate).
- explanation: A concise rationale for the correct answer(s).
"""

REWRITE_HINT = """
When reviewing your output, verify the following:
1. Fact-Check: Is the identified correct answer objectively true?
2. Clarity: Is the question stem unambiguous and free of numbering?
3. Rationale: Does the explanation provide a comprehensive justification for the correct choice?
"""
