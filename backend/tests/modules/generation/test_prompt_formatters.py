from app.modules.generation.llm.question_editor.prompts import (
    format_question_block,
    format_topic_context,
)
from app.modules.generation.llm.v1.test_generator_prompts import (
    format_topic_context as format_v1_topic_context,
)
from app.modules.generation.models import MultipleChoiceQuestion


def test_format_topic_context_wraps_non_empty_topic():
    assert format_topic_context("Biology") == "Topic domain boundary: Biology"
    assert format_v1_topic_context("Biology") == "Topic domain boundary: Biology"


def test_format_topic_context_returns_empty_for_blank_topic():
    assert format_topic_context("   ") == ""


def test_format_question_block_includes_question_fields():
    question = MultipleChoiceQuestion(
        question="What is 2 + 2?",
        options=["3", "4"],
        correct_indices=[1],
        explanation="2 + 2 = 4",
    )
    block = format_question_block(question)
    assert "question: What is 2 + 2?" in block
    assert "A. 3" in block
    assert "B. 4" in block
    assert "correct_indices: [1]" in block
    assert "explanation: 2 + 2 = 4" in block
