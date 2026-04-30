from app.services.llm.full_quiz import FullQuizLlm


def test_build_messages_with_topic_marks_topic_as_domain_only() -> None:
    messages = FullQuizLlm(
        topic="Cell biology",
        num_questions=2,
        few_shot_examples=["Case: A patient shows ATP depletion under hypoxia."],
    ).build_messages()
    user_content = messages[1]["content"]
    assert "examples must not be overshadowed by topic breadth alone" in user_content
    sys_content = messages[0]["content"]
    assert "# Guidelines" in sys_content
    assert "# Context" in sys_content
    assert sys_content.index("# Guidelines") < sys_content.index("# Context")
    assert "Topic domain boundary: Cell biology" in sys_content
    assert "Source priority (highest to lowest):" in sys_content
    assert "1) Examples (scenario style, detail level, reasoning pattern)" in sys_content
    assert "3) Topic" in sys_content
    assert "Topic is a domain label only." in sys_content
    assert "If topic conflicts with examples, keep the example pattern" in sys_content


def test_build_messages_without_topic_still_includes_priority_rules() -> None:
    messages = FullQuizLlm(
        topic="",
        num_questions=2,
        few_shot_examples=["Scenario: Evaluate trade-offs in a production outage."],
    ).build_messages()
    sys_content = messages[0]["content"]
    assert "# Guidelines" in sys_content
    assert "# Context" in sys_content
    assert "The user did not provide a topic." in sys_content
    assert "Source priority (highest to lowest):" in sys_content
    assert "examples must not be overshadowed by topic breadth alone" in messages[1]["content"]
