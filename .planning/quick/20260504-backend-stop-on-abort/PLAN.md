# Quick: backend stop on client abort

Cancel server-side quiz/question generation when the HTTP client closes the connection (frontend fetch/axios abort), so work does not continue after Stop.

- Add helper racing `Request.is_disconnected()` vs an async work coroutine; on disconnect, cancel the work task.
- Use it in `generate.py` for both generate routes; respond with HTTP 499 on client disconnect.
