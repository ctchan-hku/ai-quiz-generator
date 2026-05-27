TEST_AUTHOR_ROLE_DEFAULT = (
    "You are an expert test generation assistant that writes factually accurate multiple-choice questions."
)

TEST_SOURCE_PRIORITY_GUIDANCE = """Source priority (highest to lowest):
1) Examples (scenario style, detail level, reasoning pattern)
2) User instructions and guardrails
3) Topic

Topic is a domain label only. It defines the subject area and terminology, but does NOT override the scenario patterns from examples.

Generation policy:
- First, extract scenario/content patterns from examples (what kinds of situations are asked, what reasoning is expected).
- Then generate new questions that follow those patterns within the topic domain.
- If topic conflicts with examples, keep the example pattern and adapt entities/terms to the topic.
- Do not produce generic topic trivia when examples imply scenario-based questions."""

TEST_GENERATOR_USER_PROMPT = (
    "Task: Create exactly {num_questions} {question_type} questions. "
    "Follow these sections: # Guidelines, # Context, # Requirements, # Examples, # Chain of Thought, and # Output Format."
)

TEST_GENERATOR_FEW_SHOT_REMARK = (
    " When # Examples is non-empty, treat those lines as the strongest signal for "
    "difficulty, tone, and stem structure; use the topic only as broad coverage "
    "direction — examples must not be overshadowed by topic breadth alone."
)
