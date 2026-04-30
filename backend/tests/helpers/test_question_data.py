from app.helpers.question_data import format_question
from app.models.mc_question import MultipleChoiceQuestion


def test_format_question_for_prompt_labels_options_with_letters() -> None:
    q = MultipleChoiceQuestion(
        question_type="multiple_choice",
        question="Capital of France?",
        options=["Berlin", "Madrid", "Paris", "Rome"],
        correct_indices=[2],
        explanation="Paris is the capital.",
    )
    text = format_question(q)
    assert "A. Berlin" in text
    assert "B. Madrid" in text
    assert "C. Paris" in text
    assert "D. Rome" in text
    assert "[0]" not in text
