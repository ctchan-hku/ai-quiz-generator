import pytest

from app.modules.generation.llm.v2.generators.difficulty_target import (
    DifficultyTargetGenerator,
    DifficultyTargetPayload,
)


def test_difficulty_target_generator_parses_valid_payload() -> None:
    generator = DifficultyTargetGenerator(
        user_instructions=["Make questions moderately challenging"],
        few_shot_examples=["Example stem"],
    )

    parsed = generator.parse('{"difficulty_index": 0.62}')

    assert parsed == DifficultyTargetPayload(difficulty_index=0.62)


def test_difficulty_target_generator_rejects_out_of_range_values() -> None:
    generator = DifficultyTargetGenerator()

    with pytest.raises(ValueError):
        generator.parse('{"difficulty_index": 1.5}')


def test_difficulty_target_generator_parses_string_numeric_value() -> None:
    generator = DifficultyTargetGenerator()

    parsed = generator.parse('{"difficulty_index": "0.62"}')

    assert parsed == DifficultyTargetPayload(difficulty_index=0.62)


def test_difficulty_target_generator_user_prompt_includes_json_reminder() -> None:
    generator = DifficultyTargetGenerator()

    user_prompt = generator.build_messages()[1]["content"]

    assert "only that JSON object" in user_prompt
    assert '"difficulty_index"' in user_prompt


def test_difficulty_target_generator_system_prompt_includes_scale() -> None:
    generator = DifficultyTargetGenerator(
        user_instructions=["Keep questions at an introductory level"],
    )

    messages = generator.build_messages()
    system_prompt = messages[0]["content"]

    assert "0.0 = impossible" in system_prompt
    assert "1.0 = trivial" in system_prompt
    assert "0.40 to 0.70" in system_prompt
    assert '"difficulty_index"' in system_prompt
    assert "Chain of Thought" in system_prompt
    assert "0.0" in system_prompt
