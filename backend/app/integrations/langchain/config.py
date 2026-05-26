from typing import Literal

StructuredOutputMethod = Literal["function_calling", "json_mode", "json_schema"]

# Validated in Phase 0 spike against the OpenAI-compatible proxy; json_mode matches
# the prior CompletionParams.json_mode behavior and has the broadest gateway support.
STRUCTURED_OUTPUT_METHOD: StructuredOutputMethod = "json_mode"

LANGSMITH_PROJECT_DEFAULT = "ai-test-generator"
