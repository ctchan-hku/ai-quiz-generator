import pytest

from app.modules.data.student_stats.handlers.question_metrics_handler import (
    QuestionMetricsContext,
)
from app.modules.data.student_stats.models import (
    QuestionMetric,
    QuestionMetricsResponse,
    QuestionRecord,
    ResponseNrl,
)
from app.modules.data.student_stats.models.records import SpecificationItem
from app.modules.data.student_stats.services.question_metrics_service import (
    QuestionMetricsService,
)
from app.modules.generation.helpers.reference_selection import (
    ReferenceQuestion,
    build_reference_questions,
    distance_to_difficulty_interval,
    format_difficulty_reference_context,
    select_closest_questions,
)


def _question(
    question_id: str,
    *,
    difficulty_index: tuple[float, float],
    prompt: str = "Sample prompt",
) -> ReferenceQuestion:
    return ReferenceQuestion(
        question_id=question_id,
        prompt=prompt,
        option_labels=["A", "B", "C"],
        difficulty_index=difficulty_index,
    )


def test_distance_to_difficulty_interval_target_inside_bounds() -> None:
    assert distance_to_difficulty_interval(0.55, 0.48, 0.62) == 0.0


def test_distance_to_difficulty_interval_target_outside_bounds() -> None:
    assert distance_to_difficulty_interval(0.55, 0.60, 0.70) == pytest.approx(0.05)
    assert distance_to_difficulty_interval(0.55, 0.40, 0.50) == pytest.approx(0.05)


def test_select_closest_questions_uses_interval_distance() -> None:
    candidates = [
        _question("contains-target", difficulty_index=(0.50, 0.60)),
        _question("near", difficulty_index=(0.52, 0.54)),
        _question("far", difficulty_index=(0.10, 0.20)),
    ]

    selected = select_closest_questions(candidates, 0.55, limit=2)

    assert [question.question_id for question in selected] == [
        "contains-target",
        "near",
    ]


def test_select_closest_questions_returns_top_five_by_interval_distance() -> None:
    candidates = [
        _question("far", difficulty_index=(0.05, 0.15)),
        _question("near-2", difficulty_index=(0.51, 0.53)),
        _question("near-1", difficulty_index=(0.50, 0.52)),
        _question("mid", difficulty_index=(0.54, 0.56)),
        _question("outer", difficulty_index=(0.85, 0.95)),
        _question("near-3", difficulty_index=(0.52, 0.54)),
    ]

    selected = select_closest_questions(candidates, 0.55, limit=5)

    assert [question.question_id for question in selected] == [
        "mid",
        "near-3",
        "near-2",
        "near-1",
        "outer",
    ]


def test_select_closest_questions_returns_empty_for_no_candidates() -> None:
    assert select_closest_questions([], 0.55) == []


def test_format_difficulty_reference_context_includes_prompt_and_interval() -> None:
    selected = [
        _question(
            "q-1",
            difficulty_index=(0.48, 0.52),
            prompt="What is 2 + 2?",
        ),
    ]

    context = format_difficulty_reference_context(0.55, selected)

    assert "Target difficulty index: 0.55" in context
    assert "Reference question 1 (difficulty 0.48–0.52):" in context
    assert "Stem: What is 2 + 2?" in context
    assert "Options:" in context
    assert "- A" in context


def test_format_difficulty_reference_context_handles_empty_selection() -> None:
    context = format_difficulty_reference_context(0.55, [])

    assert "Target difficulty index: 0.55" in context
    assert "No reference questions were available" in context


def test_build_reference_questions_skips_blank_prompts() -> None:
    context = QuestionMetricsContext(
        questions=[
            QuestionRecord(
                id="q-1",
                prompt="What is 2 + 2?",
                type="mc",
                response_nrl=ResponseNrl(
                    specification=[
                        SpecificationItem(label="B) 4", value=1),
                        SpecificationItem(label="A) 3", value=0),
                    ],
                ),
            ),
            QuestionRecord(
                id="q-2",
                prompt="   ",
                type="mc",
                response_nrl=ResponseNrl(
                    specification=[
                        SpecificationItem(label="A) Yes", value=0),
                        SpecificationItem(label="B) No", value=1),
                    ],
                ),
            ),
        ],
        responses=[],
    )
    metrics = QuestionMetricsResponse(
        questions=[
            QuestionMetric(question_id="q-1", difficulty_index=[0.48, 0.52]),
            QuestionMetric(question_id="q-2", difficulty_index=[0.20, 0.30]),
        ],
    )

    def build_metrics(
        responses: list,
        questions: list[QuestionRecord],
    ) -> QuestionMetricsResponse:
        del responses, questions
        return metrics

    service = QuestionMetricsService()
    service.build_question_metrics = build_metrics  # type: ignore[method-assign]

    reference_questions = build_reference_questions(context, service)

    assert reference_questions == [
        ReferenceQuestion(
            question_id="q-1",
            prompt="What is 2 + 2?",
            option_labels=["A) 3", "B) 4"],
            difficulty_index=(0.48, 0.52),
        ),
    ]
