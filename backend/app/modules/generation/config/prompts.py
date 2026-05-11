"""LLM prompt copy, MCQ rule text, and full-quiz list-section formatters."""

from app.modules.generation.config.mc_question import (
    MC_QUESTION_EXPLANATION_SOFT_MAX_CHARS,
)
from app.modules.generation.services.section_formatter import SectionFormatter

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
