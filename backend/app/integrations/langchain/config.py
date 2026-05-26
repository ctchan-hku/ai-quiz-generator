from typing import Final, Literal

# Structured output: json_mode only.
# The API enforces a single JSON object; field shapes come from generator prompts
# (SystemPromptBuilder.output_format + structured_json_format).
StructuredOutputMethod = Literal["json_mode"]

STRUCTURED_OUTPUT_METHOD: Final[StructuredOutputMethod] = "json_mode"

LANGSMITH_PROJECT_DEFAULT = "ai-test-generator"

# Token limits
MAX_COMPLETION_TOKENS = 4096
MAX_DEBUG_COMPLETION_TOKENS = 64
DEBUG_COMPLETION_TEMPERATURE = 0.7

__all__ = [
    "DEBUG_COMPLETION_TEMPERATURE",
    "LANGSMITH_PROJECT_DEFAULT",
    "MAX_COMPLETION_TOKENS",
    "MAX_DEBUG_COMPLETION_TOKENS",
    "STRUCTURED_OUTPUT_METHOD",
    "StructuredOutputMethod",
]
