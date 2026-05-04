"""Generate routes return `cost_usd` from usage × catalog prices."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def quiz_payload() -> dict:
    return {
        "questions": [
            {
                "question_type": "multiple_choice",
                "question": "Q",
                "options": ["a", "b", "c", "d"],
                "correct_indices": [0],
                "explanation": "e",
            },
        ],
    }


@pytest.fixture
def mcq_payload() -> dict:
    return {
        "question_type": "multiple_choice",
        "question": "New?",
        "options": ["a", "b", "c", "d"],
        "correct_indices": [2],
        "explanation": "n",
    }


@pytest.fixture(autouse=True)
def patched_generate_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    catalog = [
        {"id": "cost-test-model", "label": "T", "price": {"input": 1.0, "output": 2.0}},
    ]
    fake = MagicMock()
    fake.available_model_ids = {"cost-test-model"}
    fake.available_models = catalog
    monkeypatch.setattr("app.routers.generate.settings", fake)
    # Prefer merged catalog in generate router; mirror it so tests stay deterministic.
    from app.main import app

    app.state.models_catalog = list(catalog)


def _mock_openai_for_content(payload: dict) -> AsyncMock:
    mock = AsyncMock()
    resp = MagicMock()
    resp.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]
    resp.usage = MagicMock(prompt_tokens=1_000_000, completion_tokens=500_000)
    mock.chat.completions.create = AsyncMock(return_value=resp)
    return mock


def _test_client(
    monkeypatch: pytest.MonkeyPatch,
    mock_llm: AsyncMock,
) -> TestClient:
    monkeypatch.setattr(
        "app.services.llm.full_quiz.shuffle_option_order",
        lambda opts, ci: (list(opts), list(ci)),
    )
    monkeypatch.setattr(
        "app.services.llm.single_mcq.shuffle_option_order",
        lambda opts, ci: (list(opts), list(ci)),
    )
    from app.main import app
    from app.services.llm.openai.client import get_llm_client

    app.dependency_overrides[get_llm_client] = lambda: mock_llm
    return TestClient(app)


def test_generate_quiz_includes_cost_usd(
    monkeypatch: pytest.MonkeyPatch,
    quiz_payload: dict,
) -> None:
    mock = _mock_openai_for_content(quiz_payload)
    client = _test_client(monkeypatch, mock)
    try:
        r = client.post(
            "/api/generate/quiz",
            json={
                "topic": "biology",
                "num_questions": 1,
                "model": "cost-test-model",
            },
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["cost_usd"] >= 0
        assert data["cost_usd"] == pytest.approx(2.0)
        assert len(data["questions"]) == 1
    finally:
        from app.main import app
        from app.services.llm.openai.client import get_llm_client

        app.dependency_overrides.pop(get_llm_client, None)
        client.close()


def test_generate_question_wraps_question_and_cost(
    monkeypatch: pytest.MonkeyPatch,
    mcq_payload: dict,
) -> None:
    mock = _mock_openai_for_content(mcq_payload)
    client = _test_client(monkeypatch, mock)
    try:
        body = {
            "model": "cost-test-model",
            "topic": "t",
            "question": {
                "question_type": "multiple_choice",
                "question": "Old?",
                "options": ["a", "b", "c", "d"],
                "correct_indices": [1],
                "explanation": "x",
            },
        }
        r = client.post("/api/generate/question", json=body)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "question" in data and "cost_usd" in data
        assert data["cost_usd"] >= 0
        assert data["question"]["question_type"] == "multiple_choice"
    finally:
        from app.main import app
        from app.services.llm.openai.client import get_llm_client

        app.dependency_overrides.pop(get_llm_client, None)
        client.close()
