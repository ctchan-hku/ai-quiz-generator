from app.modules.generation.config.mc_question import (
    MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS,
)

REWRITE_HINT = f"""
When reviewing your output, verify the following:
1. Fact-check: Is each identified correct answer objectively true?
2. Stem: Is the question stem unambiguous, unnumbered, and aligned with the marked correct option(s)?
3. Distractors: Are incorrect options plausible relative to the stem (same topic/vocabulary), not absurd?
4. Explanation: Does it use numbered or clearly labeled deduction steps—not a vague single sentence?
5. Length: Is each explanation roughly within ~{MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS} characters unless more is clearly needed?
"""
