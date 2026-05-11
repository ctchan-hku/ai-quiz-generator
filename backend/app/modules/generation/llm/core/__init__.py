"""Cross-version LLM pipeline primitives (shared quiz inputs and JSON chat steps)."""

from app.modules.generation.llm.core.json_prompter_parse_task import JsonPrompterParseTask
from app.modules.generation.llm.core.quiz_pipeline import BaseQuizPipeline

__all__ = ["BaseQuizPipeline", "JsonPrompterParseTask"]
