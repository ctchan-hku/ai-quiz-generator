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

INSTRUCTION_ROUTER_USER_PROMPT = (
    "Task: Route each instruction line below into one or more of `stem`, `answer`, and "
    "`distractor`. An instruction belongs in multiple arrays when more than one stage must "
    "honor it (copy duplicates verbatim into each).\n\n"
    "Stem: wording, difficulty, realism, numerical setup, notation, formatting of the QUESTION ONLY.\n"
    "Answer: solving style, derivation depth, rounding, units, how the correct result "
    "and explanation are written.\n"
    "Distractor: how wrong choices are chosen, similarity to the truth, option counts.\n\n"
    "Rules:\n"
    "- Prefer copying each line EXACTLY as written.\n"
    "- Whitespace normalization is tolerated; wording must remain the same line (no rewriting).\n"
    '- Always include `"stem": [], "answer": [], "distractor": []` arrays (empty allowed).\n'
    "- Cover every line in at least one array when verbatim copies are feasible; "
    "otherwise place the ambiguous line conservatively across `stem`, `answer`, and `distractor` "
    "as needed.\n\n"
    "Instructions to route:\n{instructions_block}"
)
