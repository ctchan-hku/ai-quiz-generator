from app.features.generation.llm.v2.generators.answer.generator import (
    AnswerGenerator,
    AnswersPayload,
)
from app.integrations.langchain.structured_step import _parse_repaired_raw

INVALID_LATEX_JSON = (
    '{\n  "items": [\n'
    '    {"answer": "13/30 km", "explanation": "Use \\frac{x}{5} and \\sin(\\pi)."},\n'
    '    {"answer": "x = 1", "explanation": "Check \\sqrt{2} and \\lim_{x \\to 1}."}\n'
    "  ]\n"
    "}"
)


def test_parse_repaired_raw_fixes_unescaped_latex_json():
    generator = AnswerGenerator(stems=["q1", "q2"])
    parsed = _parse_repaired_raw(
        INVALID_LATEX_JSON,
        AnswersPayload,
        generator.post_process,
    )

    assert len(parsed.items) == 2
    assert "\\frac" in parsed.items[0].explanation
    assert "\\sin" in parsed.items[0].explanation
