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

QUESTION_STEM_GENERATOR_USER_PROMPT = (
    "Task: Create exactly {num_stems} question stems on topic: {topic_line}. "
    "Output only the stems in JSON as specified — no answers, options, or explanations."
)
