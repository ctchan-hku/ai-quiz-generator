from app.modules.generation.config.mc_question import (
    MC_QUESTION_OPTION_COUNT_DEFAULT,
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)

QUESTION_STEM_GENERATOR_ROLE_DEFAULT = (
    "You design assessment question stems that measure how well students understand a topic. "
    "Use whatever question style fits the examples and topic; you are not limited to multiple choice."
)

QUESTION_STEM_GENERATOR_FEW_SHOT_REMARK = (
    " When # Examples is non-empty, treat those lines as the strongest signal for "
    "question style, tone, phrasing, and background context; use the topic only as "
    "broad coverage direction — examples must not be overshadowed by topic breadth alone."
)

QUESTION_STEM_GENERATOR_DIFFICULTY_CONTEXT_REMARK = (
    " When # Context includes difficulty reference material, use it only to calibrate "
    "how challenging the stems should be. Follow # Examples for question style and "
    "background context — do not copy reference stems for wording or option layout."
)

QUESTION_STEM_GENERATOR_DIFFICULTY_CHAIN_OF_THOUGHT = """Before writing stems:
1) Read # Context first. Identify the target difficulty index and use the reference questions only as difficulty calibration — how hard comparable items were for students, not as templates for wording or format.
2) Read # Examples next. Match their question style, tone, phrasing, and subject background context when drafting new stems.
3) Apply # Requirements and the topic for coverage and constraints."""

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

INSTRUCTION_ROUTER_ROLE_DEFAULT = (
    "You are a precise taxonomy assistant for pedagogical authoring pipelines. "
    "Given a numbered list of user requirements, classify each requirement into stem, "
    "answer-stage, distractor-stage, or overlapping combinations. Output only structured JSON "
    "and copy requirement text verbatim from the numbered list."
)

INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT = """Routing rules:
1) Read every numbered line independently; ambiguity is allowed—overlap stems and answer when both must comply.
2) Stem covers scenario setup, realism, wording, learner level, STEM context, diagrams implied in text, numbering style.
3) Answer covers solution rigor, step-by-step explanation detail, arithmetic layout, rounding, justification tone.
4) Distractor covers wrong-choice strategy, misconception targeting, parallelism with option wording, forbidden patterns.
5) When a clause bundles multiple intents, duplicate the exact sentence into each applicable array instead of rewriting.
6) Never invent new bullets; arrays only contain verbatim copies drawn from the user list."""

ANSWER_GENERATOR_ROLE_DEFAULT = (
    "You are an expert in reasoning and solving problems. "
    "You give accurate, exact final answers and keep every derivation, step, and calculation out of the answer field."
)

ANSWER_GENERATOR_CHAIN_OF_THOUGHT = """Work like an expert solver:
1) Read each question and decide what quantity or conclusion it asks for.
2) Plan the method (definitions, formulas, logic, or elimination) before computing.
3) Execute carefully; for numeric tasks show arithmetic in the `explanation` field only, not in the `answer` field.
4) State the `answer` field as the precise result the question expects (short phrase, value, or name—no trailing reasoning).
5) Put every intermediate step, justification, and check in the `explanation` field so the answer line stays clean."""

DISTRACTOR_GENERATOR_ROLE_DEFAULT = (
    "You are an expert assessment designer who writes plausible incorrect options (distractors) "
    "for multiple-choice questions. Distractors must be wrong yet tempting, must not duplicate "
    "or paraphrase the correct answer, and each distractor must be only the incorrect choice wording—"
    'no reasoning, derivation, rationale, commentary, prefixes (e.g. "Wrong:"), '
    "or parentheses that explain why it is incorrect."
)

DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT = """When inventing distractors:
1) Use the stem to judge format, domain, and difficulty (units, precision, vocabulary).
2) Use the correct answer and explanation only as private reasoning—do not copy reasoning into any option text.
3) Each distractor should be incorrect but credible to a student who partially misunderstands.
4) Keep options mutually distinct; avoid absurd or joke answers unless the stem is informal.
5) Match the style and length of the correct answer (e.g. numeric vs short phrase).
6) Emit nothing in `distractors` except strings that could appear verbatim on an answer sheet—the same kind of content as the correct answer field, with zero explanation appended.
7) Do not write free-form solutions or commentary outside the JSON object; put nothing outside `items`."""


def distractor_structured_json_format() -> str:
    return '{\n  "items": [\n    {"distractors": ["...", "..."]},\n    ...\n  ]\n}'


def format_distractor_user_prompt_intro(num_questions: int) -> str:
    min_wrong = MC_QUESTION_OPTION_COUNT_MIN - 1
    max_wrong = MC_QUESTION_OPTION_COUNT_MAX - 1
    default_wrong = MC_QUESTION_OPTION_COUNT_DEFAULT - 1
    total_default = MC_QUESTION_OPTION_COUNT_DEFAULT
    return (
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
