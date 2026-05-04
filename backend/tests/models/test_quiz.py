"""LLM parse envelope `Quiz` (`quiz.py`)."""

from app.models.mc_question import MultipleChoiceQuestion
from app.models.quiz import Quiz


def test_quiz_is_list_of_mcq() -> None:
    q = MultipleChoiceQuestion(
        question_type="multiple_choice",
        question="?",
        options=["a", "b", "c", "d"],
        correct_indices=[0],
        explanation="e",
    )
    quiz = Quiz(questions=[q])
    assert len(quiz.questions) == 1
    assert quiz.questions[0].question == "?"
