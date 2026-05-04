"""Pydantic schemas for quiz envelope and generate responses."""

from app.models.mc_question import MultipleChoiceQuestion
from app.models.schemas import QuestionGenerateResponse, QuizResponse


def test_quiz_response_includes_cost_usd() -> None:
    q = MultipleChoiceQuestion(
        question_type="multiple_choice",
        question="?",
        options=["a", "b", "c", "d"],
        correct_indices=[0],
        explanation="e",
    )
    r = QuizResponse(
        questions=[q],
        model_used="m",
        source="topic",
        cost_usd=0.0,
    )
    assert r.cost_usd == 0.0


def test_question_generate_response_shape() -> None:
    q = MultipleChoiceQuestion(
        question_type="multiple_choice",
        question="?",
        options=["a", "b", "c", "d"],
        correct_indices=[0],
        explanation="e",
    )
    r = QuestionGenerateResponse(question=q, cost_usd=1.5)
    assert r.cost_usd == 1.5
    assert r.question.question == "?"
