"""Prompt copy for version-2 multi-step generators (stems → answers → distractors)."""

from app.modules.generation.config.mc_question import (
    MC_QUESTION_OPTION_COUNT_DEFAULT,
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)

QUESTION_GENERATOR_ROLE_DEFAULT = (
    "You design assessment questions that measure how well students understand a topic. "
    "Use whatever question style fits the examples and topic; you are not limited to multiple choice."
)

QUESTION_GENERATOR_FEW_SHOT_REMARK = (
    " When # Examples is non-empty, treat those lines as the strongest signal for "
    "difficulty, tone, and stem structure; use the topic only as broad coverage "
    "direction — examples must not be overshadowed by topic breadth alone."
)

ANSWER_GENERATOR_ROLE_DEFAULT = (
    "You are an expert in reasoning and solving problems. "
    "You give accurate, exact final answers and keep every derivation, step, and calculation out of the answer field."
)

ANSWER_GENERATOR_CHAIN_OF_THOUGHT = """Work like an expert solver:
1) Read each question and decide what quantity or conclusion it asks for.
2) Plan the method (definitions, formulas, logic, or elimination) before computing.
3) Execute carefully; for numeric tasks show arithmetic in the explanation only, not in the answer.
4) State the `answer` as the precise result the question expects (short phrase, value, or name—no trailing reasoning).
5) Put every intermediate step, justification, and check in `explanation` so the answer line stays clean."""

DISTRACTOR_GENERATOR_ROLE_DEFAULT = (
    "You are an expert assessment designer who writes plausible incorrect options (distractors) "
    "for multiple-choice questions. Distractors must be wrong yet tempting, must not duplicate "
    "or paraphrase the correct answer, and each distractor must be only the incorrect choice wording—"
    "no reasoning, derivation, rationale, commentary, prefixes (e.g. \"Wrong:\"), "
    'or parentheses that explain why it is incorrect.'
)

DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT = """When inventing distractors:
1) Use the stem to judge format, domain, and difficulty (units, precision, vocabulary).
2) Use the correct answer and explanation only as private reasoning—do not copy reasoning into any option text.
3) Each distractor should be incorrect but credible to a student who partially misunderstands.
4) Keep options mutually distinct; avoid absurd or joke answers unless the stem is informal.
5) Match the style and length of the correct answer (e.g. numeric vs short phrase).
6) Emit nothing in `distractors` except strings that could appear verbatim on an answer sheet—the same kind of content as the correct answer field, with zero explanation appended."""


def distractor_structured_json_format() -> str:
    min_wrong = MC_QUESTION_OPTION_COUNT_MIN - 1
    max_wrong = MC_QUESTION_OPTION_COUNT_MAX - 1
    default_wrong = MC_QUESTION_OPTION_COUNT_DEFAULT - 1
    total_default = MC_QUESTION_OPTION_COUNT_DEFAULT
    return (
        "{\n"
        '  "distractor_sets": [\n'
        "    {\n"
        f'      "distractors": ["<incorrect answer-choice text ONLY ({min_wrong}–{max_wrong} strings per item; '
        f"default {default_wrong} wrong options i.e. {total_default} total including correct)—each string is ONLY "
        "the wrong answer wording like the correct answer line; "
        'no rationales, "because ...", derivation, or parenthetical notes>"]\n'
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}"
    )


def format_distractor_user_prompt_intro(num_questions: int) -> str:
    min_wrong = MC_QUESTION_OPTION_COUNT_MIN - 1
    max_wrong = MC_QUESTION_OPTION_COUNT_MAX - 1
    default_wrong = MC_QUESTION_OPTION_COUNT_DEFAULT - 1
    total_default = MC_QUESTION_OPTION_COUNT_DEFAULT
    return (
        f"For each numbered block above, output exactly one object in `distractor_sets` in the same order.\n"
        f"There must be exactly {num_questions} entries in `distractor_sets`.\n"
        f"Each object's `distractors` must contain between {min_wrong} and {max_wrong} "
        "incorrect but plausible answer strings only (distinct from each other and from the correct answer). "
        "Do not embed explanations, step-by-step reasoning, labels, or commentary inside any distractor string.\n"
        f"Default target: exactly {default_wrong} distractors "
        f"({total_default} options total including the correct answer). "
        "If # Requirements specifies a distinct "
        "total number of choices or wrong options, match that count instead (still within the allowed range).\n\n"
    )
