"""LLM prompt copy, MCQ rule text, and full-quiz list-section formatters."""

from app.modules.generation.services.section_formatter import SectionFormatter

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
        "User-provided requirements — adhere to these specific instructions and preferences during question generation. "
        "These override defaults but should complement the reference examples' style:\n"
    ),
)

JSON_OUTPUT_RULES = (
    "Output channel: your entire assistant message must be exactly one JSON object matching the shape below.\n"
    "No ambiguity. No parsing headaches. Production-ready.\n"
    "Do not write markdown headings, prose introductions, problem walkthroughs, or ``` code fences outside that object.\n"
    "Do not wrap the payload in quotes or add any characters before `{` or after the closing `}`."
)

JSON_OUTPUT_REMINDER = "Your assistant message must contain only that JSON object—no preamble, no postscript."
