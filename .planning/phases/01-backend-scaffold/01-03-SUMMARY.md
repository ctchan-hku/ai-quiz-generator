---
plan: 01-03
title: Debug Route (`POST /api/debug/chat-completion`)
status: complete
---

# Plan 03 Summary

**Objective:** Implement the gated LLM smoke route that mounts only when `ENABLE_DEBUG_CHAT_COMPLETION=true`, uses an allowlisted model, and hard-caps tokens at 64.

## What was built
- Created `routers/debug.py` with the `/api/debug/chat-completion` route
- Verified the requested model against `settings.available_model_ids`
- Passed requests to `openai-hk.com` using `AsyncOpenAI`
- Conditionally mounted the router in `main.py` only if `enable_debug_chat_completion` is True
- Hard-capped tokens to 64 and extracted magic numbers into constants

## Key Files Created/Modified
- `backend/app/routers/debug.py`
- `backend/app/main.py`

## Self-Check: PASSED
