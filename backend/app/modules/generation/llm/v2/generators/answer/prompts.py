from app.modules.generation.llm.shared.prompts import JSON_OUTPUT_REMINDER

ROLE = (
    "You are an expert in reasoning and solving problems. "
    "You give accurate, exact final answers and keep every derivation, step, and calculation out of the answer field."
)

CHAIN_OF_THOUGHT = """Work like an expert solver:
1) Read each question and decide what quantity or conclusion it asks for.
2) Plan the method (definitions, formulas, logic, or elimination) before computing.
3) Execute carefully; for numeric tasks show arithmetic in the `explanation` field only, not in the `answer` field.
4) State the `answer` field as the precise result the question expects (short phrase, value, or name—no trailing reasoning).
5) Put every intermediate step, justification, and check in the `explanation` field so the answer line stays clean."""

STRUCTURED_JSON_FORMAT = (
    "{\n"
    '  "items": [\n'
    '    {"answer": "...", "explanation": "..."},\n'
    "    ...\n"
    "  ]\n"
    "}"
)

USER_PROMPT = (
    "Solve each question below. Return exactly {num_questions} objects in `items`, in the same order as listed.\n\n"
    "Questions:\n{numbered_questions}\n\n"
    "The `answer` field must be the exact final result only—no steps or commentary there. "
    "Put all reasoning, derivation, and calculations in `explanation`.\n\n"
    f"{JSON_OUTPUT_REMINDER}"
)
