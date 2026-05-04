"""POST /api/generate/question response envelope (`question` + `cost_usd`)."""

from app.models.schemas import QuestionGenerateResponse


def test_question_generate_response_shape() -> None:
    from app.models.mc_question import MultipleChoiceQuestion

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
