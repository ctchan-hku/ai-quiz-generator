from app.modules.similarity.prompts import format_embeddable_question


def test_format_embeddable_question_includes_prompt_and_options():
    text = format_embeddable_question(
        prompt="What is 2 + 2?",
        options=["3", "4", "5"],
    )
    assert "What is 2 + 2?" in text
    assert "3" in text
    assert "4" in text
    assert "5" in text


def test_format_embeddable_question_skips_blank_prompt():
    assert format_embeddable_question(prompt="   ", options=["A"]) == ""
