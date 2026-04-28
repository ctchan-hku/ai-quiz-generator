---
status: complete
---

Replaced `json.dumps(messages)` with `_format_messages_readable`: each turn on its own section, string content keeps actual newlines; non-string `content` uses indented JSON. Fallback `repr(messages)` on any formatting error. Backend `pytest`: 34 passed.
