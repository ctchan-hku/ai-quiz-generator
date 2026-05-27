from app.modules.generation.config.mc_question import (
    MC_QUESTION_OPTION_COUNT_DEFAULT,
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.llm.shared.prompts import JSON_OUTPUT_REMINDER

ROLE = (
    "You are an expert assessment designer who writes plausible incorrect options (distractors) "
    "for multiple-choice questions. Distractors must be wrong yet tempting, must not duplicate "
    "or paraphrase the correct answer, and each distractor must be only the incorrect choice wording—"
    'no reasoning, derivation, rationale, commentary, prefixes (e.g. "Wrong:"), '
    "or parentheses that explain why it is incorrect."
)

CHAIN_OF_THOUGHT = """When inventing distractors:
1) Use the stem to judge format, domain, and difficulty (units, precision, vocabulary).
2) Use the correct answer and explanation only as private reasoning—do not copy reasoning into any option text.
3) Each distractor should be incorrect but credible to a student who partially misunderstands.
4) Keep options mutually distinct; avoid absurd or joke answers unless the stem is informal.
5) Match the style and length of the correct answer (e.g. numeric vs short phrase).
6) Emit nothing in `distractors` except strings that could appear verbatim on an answer sheet—the same kind of content as the correct answer field, with zero explanation appended.
7) Do not write free-form solutions or commentary outside the JSON object; put nothing outside `items`."""

STRUCTURED_JSON_FORMAT = (
    '{\n  "items": [\n    {"distractors": ["...", "..."]},\n    ...\n  ]\n}'
)


def format_user_prompt(num_questions: int, question_blocks: str) -> str:
    min_wrong = MC_QUESTION_OPTION_COUNT_MIN - 1
    max_wrong = MC_QUESTION_OPTION_COUNT_MAX - 1
    default_wrong = MC_QUESTION_OPTION_COUNT_DEFAULT - 1
    total_default = MC_QUESTION_OPTION_COUNT_DEFAULT
    intro = (
        f"For each numbered block above, output exactly one object in `items` in the same order.\n"
        f"There must be exactly {num_questions} entries in `items`.\n"
        f"Each object's `distractors` must contain between {min_wrong} and {max_wrong} "
        "incorrect but plausible answer strings only (distinct from each other and from the correct answer). "
        "Do not embed explanations, step-by-step reasoning, labels, or commentary inside any distractor string.\n"
        f"Default target: exactly {default_wrong} distractors "
        f"({total_default} options total including the correct answer). "
        "If # Requirements specifies a distinct "
        "total number of choices or wrong options, match that count instead (still within the allowed range).\n\n"
    )
    return intro + question_blocks + "\n\n" + JSON_OUTPUT_REMINDER
