from typing import Any, Type, get_args

from openai import AsyncOpenAI
from pydantic.fields import PydanticUndefined

from app.config import settings
from app.models.schemas import BaseQuestion, MultipleChoiceQuestion
from app.services.few_shot import format_few_shot_system_section


def _question_type_literal(question_class: Type[BaseQuestion]) -> str:
    field = question_class.model_fields["question_type"]
    if field.default is not None and field.default is not PydanticUndefined:
        return str(field.default)
    args = get_args(field.annotation)
    if args:
        return str(args[0])
    raise TypeError(f"Cannot resolve question_type for {question_class.__name__}")


SYSTEM_PROMPT_HEADER = (
    "You are a quiz generation assistant. Your ONLY output must be a raw JSON object containing a single key "
    "'questions' that holds an array of question objects.\n"
    "Do not include markdown, explanation, or any text outside the JSON object."
)

MAX_COMPLETION_TOKENS = 4096
COMPLETION_TEMPERATURE = 0.7

# Merge with {"model": <id>} for a full chat.completions.create kwargs dict.
CHAT_COMPLETION_KWARGS: dict[str, Any] = {
    "response_format": {"type": "json_object"},
    "temperature": COMPLETION_TEMPERATURE,
    "max_tokens": MAX_COMPLETION_TOKENS,
}


def get_llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=55,
    )


def build_messages(
    topic: str,
    num_questions: int,
    question_class: Type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
    few_shot_examples: list[str] | None = None,
) -> list[dict[str, Any]]:
    qtype = _question_type_literal(question_class)

    full_system_prompt = f"{SYSTEM_PROMPT_HEADER}\n\n{question_class.system_prompt}"
    if few_shot_examples:
        full_system_prompt = (
            f"{full_system_prompt}\n\n{format_few_shot_system_section(few_shot_examples)}"
        )

    return [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": f"Generate {num_questions} {qtype} questions about: {topic}"},
    ]


async def generate_quiz(
    topic: str,
    num_questions: int,
    model: str,
    client: AsyncOpenAI,
    question_class: Type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
    few_shot_examples: list[str] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    messages = build_messages(topic, num_questions, question_class, few_shot_examples=few_shot_examples)
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
        **CHAT_COMPLETION_KWARGS,
    )
    raw = response.choices[0].message.content or ""
    return raw, messages
