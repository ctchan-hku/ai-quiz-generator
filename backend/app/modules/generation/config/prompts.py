"""Full-quiz list-section formatters and shared prompt intros."""

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
        "User-specific requirements—apply these constraints and preferences when generating questions. "
        "These override defaults but should complement the reference examples' style:\n"
    ),
)
