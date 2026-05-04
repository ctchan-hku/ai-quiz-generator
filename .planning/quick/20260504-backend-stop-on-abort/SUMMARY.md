---
status: complete
---

# Quick task: backend stop on client abort

**Scope:** Cancel LLM pipeline on `POST /api/generate/quiz` and `POST /api/generate/question` when the client disconnects (e.g. frontend `AbortController`), using `Request.is_disconnected()` and asyncio task cancellation.

**Delivered:**

- `app/helpers/client_disconnect.py` — `cancel_on_client_disconnect`, `ClientDisconnectedError`
- `app/routers/generate.py` — wrap generation + parse/retry in inner async functions, race against disconnect; map to **HTTP 499** when client gone (nginx convention)
- `tests/helpers/test_client_disconnect.py` — unit tests for cancel vs success paths

**Note:** Upstream OpenAI may still bill for a request already accepted; this stops the **app** from awaiting further work when the browser aborts.
