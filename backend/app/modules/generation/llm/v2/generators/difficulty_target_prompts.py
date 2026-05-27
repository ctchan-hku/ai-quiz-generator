from app.modules.generation.llm.shared.prompts import JSON_OUTPUT_REMINDER

DIFFICULTY_TARGET_ROLE_DEFAULT = (
    "You infer the intended assessment difficulty from user instructions and few-shot "
    "examples. Output a single difficulty index on a 0.0–1.0 scale."
)

DIFFICULTY_TARGET_GUIDELINES = """Difficulty index scale:
- 0.0 = impossible (no students answered correctly)
- 1.0 = trivial (every student answered correctly)
- Optimal classroom range: 0.40 to 0.70 (medium difficulty)"""

DIFFICULTY_TARGET_CHAIN_OF_THOUGHT = """When choosing the index:
1) Read user instructions and few-shot examples for explicit difficulty cues (easy, hard, advanced, introductory, etc.).
2) When no difficulty is specified, choose one index inside 0.40–0.70 (prefer near 0.55).
3) When difficulty is implied, map it to a single index on the scale.
4) Emit only the JSON object below with one numeric `difficulty_index` field — no prose, markdown, or extra keys."""


def difficulty_target_structured_json_format() -> str:
    return '{\n  "difficulty_index": 0.0\n}'


DIFFICULTY_TARGET_USER_PROMPT = (
    "Task: Determine the single target difficulty index for new questions "
    "based on the user instructions and few-shot examples in the system message.\n\n"
    'Return exactly one JSON object with one numeric field `"difficulty_index"` '
    "between 0.0 and 1.0 inclusive. Do not quote the number as a string.\n\n"
    f"{JSON_OUTPUT_REMINDER}"
)
