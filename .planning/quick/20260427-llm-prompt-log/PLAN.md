# Quick: log full LLM chat messages (opt-in)

**Goal:** When debugging, see the complete `messages` list sent to `chat.completions` for quiz generation and for `parse_with_retry`.

**Approach:** `LOG_FULL_LLM_PROMPT` env + `app/llm_debug_log.py` called from `generate_quiz` and `parse_with_retry`.
