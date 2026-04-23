from typing import Any, Type, get_args

from openai import AsyncOpenAI
from pydantic.fields import PydanticUndefined

from app.config import settings
from app.models.schemas import BaseQuestion, MultipleChoiceQuestion


def _question_type_literal(question_class: Type[BaseQuestion]) -> str:
    field = question_class.model_fields["question_type"]
    if field.default is not None and field.default is not PydanticUndefined:
        return str(field.default)
    args = get_args(field.annotation)
    if args:
        return str(args[0])
    raise TypeError(f"Cannot resolve question_type for {question_class.__name__}")


SYSTEM_PROMPT_HEADER = (
    "You are a quiz generation assistant. Your ONLY output is a raw JSON array of questions. "
    "Do not include markdown, explanation, or any text outside the JSON array."
)

MAX_QUIZ_COMPLETION_TOKENS = 4096
QUIZ_COMPLETION_TEMPERATURE = 0.7


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
) -> list[dict[str, Any]]:
    qtype = _question_type_literal(question_class)
    
    full_system_prompt = f"{SYSTEM_PROMPT_HEADER}\n\n{question_class.system_prompt}"
    
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
) -> tuple[str, list[dict[str, Any]]]:
    messages = build_messages(topic, num_questions, question_class)
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=QUIZ_COMPLETION_TEMPERATURE,
        max_tokens=MAX_QUIZ_COMPLETION_TOKENS,
    )
    raw = response.choices[0].message.content or ""
    return raw, messages
