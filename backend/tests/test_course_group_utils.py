from app.modules.data.student_stats.constants import EXCLUDED_NAME_TERMS
from app.modules.data.student_stats.utils import name_contains_excluded_term


def test_name_contains_excluded_term_is_case_insensitive() -> None:
    assert name_contains_excluded_term("COPY - MATH1013", EXCLUDED_NAME_TERMS)
    assert name_contains_excluded_term("fake MATH1013", EXCLUDED_NAME_TERMS)
    assert not name_contains_excluded_term(
        "MATH1013 2021-2022 Sem 1 - 1",
        EXCLUDED_NAME_TERMS,
    )


def test_name_contains_excluded_term_matches_substring() -> None:
    assert name_contains_excluded_term("Demo COPY sheet", EXCLUDED_NAME_TERMS)


def test_name_contains_excluded_term_accepts_custom_terms() -> None:
    assert name_contains_excluded_term("Draft course", ("draft",))
    assert not name_contains_excluded_term("Published course", ("draft",))
