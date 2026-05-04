import asyncio

import pytest
from starlette.requests import Request

from app.helpers.client_disconnect import ClientDisconnectedError, cancel_on_client_disconnect


class _FakeRequest:
    """Minimal ``Request`` stand-in: only ``is_disconnected`` is used."""

    def __init__(self, disconnect_after_polls: int) -> None:
        self._polls = 0
        self._threshold = disconnect_after_polls

    async def is_disconnected(self) -> bool:
        self._polls += 1
        return self._polls >= self._threshold


@pytest.mark.asyncio
async def test_cancel_on_client_disconnect_cancels_pending_work() -> None:
    request: Request = _FakeRequest(4)  # type: ignore[assignment]
    started = asyncio.Event()

    cancelled = asyncio.Event()

    async def slow_work() -> str:
        started.set()
        try:
            await asyncio.sleep(60.0)
        except asyncio.CancelledError:
            cancelled.set()
            raise
        return "done"

    with pytest.raises(ClientDisconnectedError):
        await cancel_on_client_disconnect(request, slow_work())

    assert started.is_set()
    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_cancel_on_client_disconnect_returns_work_result_when_client_stays() -> None:
    class _StayConnected:
        async def is_disconnected(self) -> bool:
            return False

    request: Request = _StayConnected()  # type: ignore[assignment]

    async def fast_work() -> str:
        return "ok"

    out = await cancel_on_client_disconnect(request, fast_work())
    assert out == "ok"
