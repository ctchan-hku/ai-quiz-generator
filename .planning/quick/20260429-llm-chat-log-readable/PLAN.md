# Quick: readable LLM chat debug log

**Goal:** With `LOG_FULL_LLM_PROMPT=true`, backend logs should show each message with real line breaks and clear delimiters instead of one JSON blob where newlines appear as `\n` inside strings.

**Change:** `app/llm_debug_log.py` — per-message blocks (`── message N · role=… ──`) and raw `content` text; optional `other fields` JSON for non-standard keys.
