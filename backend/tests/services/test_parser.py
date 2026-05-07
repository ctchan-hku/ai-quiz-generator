"""Tests for parse helpers: strip_fences and parse_llm_with_retry."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.token_usage import TokenUsage
from app.modules.generation.services.parser import parse_llm_with_retry, strip_fences


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('```json\n{"a": 1}\n```', '{"a": 1}'),
        ('```JSON\n{"a": 1}\n```', '{"a": 1}'),
        ("```\n[1, 2]\n```", "[1, 2]"),
        ('  {"x": 1}  ', '{"x": 1}'),
        ("no fences here", "no fences here"),
    ],
)
def test_strip_fences_removes_markdown_wrapper(raw: str, expected: str) -> None:
    assert strip_fences(raw) == expected


def test_parse_llm_with_retry_success_returns_initial_usage() -> None:
    async def run() -> None:
        client = AsyncMock()
        u0 = TokenUsage(prompt_tokens=10, completion_tokens=20)
        out, total = await parse_llm_with_retry(
            '{"x": 1}',
            client,
            [],
            parse=json.loads,
            chat_completion_kwargs={"model": "m"},
            initial_usage=u0,
        )
        assert out == {"x": 1}
        assert total.prompt_tokens == 10
        assert total.completion_tokens == 20
        client.chat.completions.create.assert_not_called()

    asyncio.run(run())


def test_parse_llm_with_retry_merges_retry_usage() -> None:
    async def run() -> None:
        client = AsyncMock()
        retry_resp = MagicMock()
        retry_resp.choices = [MagicMock(message=MagicMock(content='{"ok": true}'))]
        retry_resp.usage = MagicMock(prompt_tokens=5, completion_tokens=7)
        client.chat.completions.create = AsyncMock(return_value=retry_resp)

        u0 = TokenUsage(prompt_tokens=100, completion_tokens=200)

        def parse(s: str) -> dict:
            if s == "not-json":
                raise json.JSONDecodeError("expecting value", s, 0)
            return json.loads(s)

        out, total = await parse_llm_with_retry(
            "not-json",
            client,
            [{"role": "user", "content": "hi"}],
            parse=parse,
            chat_completion_kwargs={"model": "m"},
            initial_usage=u0,
        )
        assert out == {"ok": True}
        assert total.prompt_tokens == 105
        assert total.completion_tokens == 207
        client.chat.completions.create.assert_called_once()

    asyncio.run(run())
