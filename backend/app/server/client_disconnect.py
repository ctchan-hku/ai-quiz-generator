"""Cancel slow API work when the browser or client closes the connection first."""

from __future__ import annotations

import asyncio
from typing import Coroutine, TypeVar

from starlette.requests import Request

T = TypeVar("T")

DISCONNECT_POLL_INTERVAL_S = 0.05


class ClientDisconnectedError(Exception):
    pass


async def _until_disconnect(request: Request) -> None:
    while not await request.is_disconnected():
        await asyncio.sleep(DISCONNECT_POLL_INTERVAL_S)


async def cancel_on_client_disconnect(
    request: Request, work: Coroutine[None, None, T]
) -> T:
    work_task = asyncio.create_task(work)
    disconnect_task = asyncio.create_task(_until_disconnect(request))
    try:
        done, _ = await asyncio.wait(
            {work_task, disconnect_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if work_task in done:
            return work_task.result()

        work_task.cancel()
        try:
            await work_task
        except asyncio.CancelledError:
            pass
        raise ClientDisconnectedError()
    finally:
        disconnect_task.cancel()
        await asyncio.gather(work_task, disconnect_task, return_exceptions=True)
