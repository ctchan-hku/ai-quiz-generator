"""LLM system and follow-up prompt text."""

from app.models.schemas import CORRECT_INDICES_COUNT, MULTIPLE_CHOICE_OPTIONS_COUNT

ROLE_DEFINITION = """You are a specialized Quiz Generation Assistant. Your goal is to produce high-quality, factually accurate, and unambiguous questions based on provided source material"""


MULTIPLE_CHOICE_INSTRUCTIONS = f"""
Each multiple-choice question object must contain:
- question_type: "multiple_choice"
- question: The stem (no numbering).
- options: A list of exactly {MULTIPLE_CHOICE_OPTIONS_COUNT} unique strings.
- correct_indices: A list containing exactly {CORRECT_INDICES_COUNT} integer index (from 0 to {MULTIPLE_CHOICE_OPTIONS_COUNT - 1}).
- explanation: A concise rationale for the correct choice.
"""

REWRITE_HINT = """
When reviewing your output, verify the following:
1. Fact-Check: Is the identified correct answer objectively true?
2. Clarity: Is the question stem unambiguous and free of numbering?
3. Rationale: Does the explanation provide a comprehensive justification for the correct choice?
"""
