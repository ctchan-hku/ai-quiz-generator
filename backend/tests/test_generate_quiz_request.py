"""Generate quiz request validation and response shape."""

import pytest
from pydantic import ValidationError

from app.models.generate_requests import GenerateQuizRequest
from app.models.schemas import QuizResponse


def test_generate_quiz_request_requires_topic_or_few_shot() -> None:
    with pytest.raises(ValidationError):
        GenerateQuizRequest(topic="", num_questions=1, model="m")


def test_quiz_response_requires_cost_usd() -> None:
    from app.models.mc_question import MultipleChoiceQuestion

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
