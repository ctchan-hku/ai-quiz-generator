"""Cross-version LLM pipeline primitives (shared quiz inputs and JSON chat steps)."""

from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.core.quiz_pipeline import BaseQuizPipeline

__all__ = ["BaseQuizPipeline", "LlmJsonGenerator"]
