"""MCQ limits and long rule strings shared by models and prompts (avoids import cycles)."""

MC_QUESTION_OPTION_COUNT_MIN = 2
MC_QUESTION_OPTION_COUNT_MAX = 6
MC_QUESTION_OPTION_COUNT_DEFAULT = 4
MC_QUESTION_CORRECT_INDICES_MIN_COUNT = 1
MC_QUESTION_EXPLANATION_TARGET_CHARS = 1000
MC_QUESTION_EXPLANATION_MAX_CHARS = 1500

GUARDRAILS = f"""Each multiple-choice question object must satisfy all rules below.

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
  - Aim for roughly {MC_QUESTION_EXPLANATION_TARGET_CHARS} characters.
"""

CHAIN_OF_THOUGHT = """Follow this order:
1. Generate the question stem.
2. Deduce the correct result from the stem.
3. Write deduction steps and final result in explanation.
4. Create one option that matches the final result exactly.
5. Create distractor options to fill the required count (plausible near-miss or similar alternatives).
6. Set correct_indices to the zero-based position(s) of the true option(s).
7. Final check: explanation result, correct option value, and correct_indices must be consistent."""
