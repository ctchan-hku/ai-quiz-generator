from typing import Annotated, ClassVar, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

MULTIPLE_CHOICE_OPTIONS_COUNT = 4
TRUE_FALSE_OPTIONS_COUNT = 2
CORRECT_INDICES_COUNT = 1
MIN_OPTIONS_COUNT = 2
MIN_CORRECT_INDICES_COUNT = 1


class BaseQuestion(BaseModel):
    """Shared quiz-question fields and LLM prompt prefix for all variants.

    Variant classes set `system_prompt` by composing `base_system_prompt` with
    type-specific schema rules (single source of truth for the common intro).
    """

    base_system_prompt: ClassVar[str] = (
        "General Rules:\n"
        "- Each question must be unambiguous and factually grounded\n"
        "- Do not number the question"
    )

    question_type: str
    question: str
    explanation: str


class OptionsQuestion(BaseQuestion):
    options: list[str]
    correct_indices: list[int]


class SingleAnswerQuestion(OptionsQuestion):
    expected_options_count: ClassVar[int]

    @field_validator("options")
    @classmethod
    def exact_options_count(cls, v: list[str]) -> list[str]:
        if len(v) != cls.expected_options_count:
            raise ValueError(f"{cls.__name__} requires exactly {cls.expected_options_count} options, got {len(v)}")
        return v

    @field_validator("correct_indices")
    @classmethod
    def single_correct_index(cls, v: list[int]) -> list[int]:
        if len(v) != CORRECT_INDICES_COUNT:
            raise ValueError(f"{cls.__name__} correct_indices must have exactly {CORRECT_INDICES_COUNT} element, got {len(v)}")
        return v


_MULTIPLE_CHOICE_SYSTEM_PROMPT_SUFFIX = f"""
Each question must have EXACTLY this shape:
{{
  "question_type": "multiple_choice",
  "question": "<question text>",
  "options": ["<A>", "<B>", "<C>", "<D>"],
  "correct_indices": [<single integer 0-3>],
  "explanation": "<one sentence explaining the correct answer>"
}}

Rules:
- Exactly {MULTIPLE_CHOICE_OPTIONS_COUNT} options per question
- correct_indices is an array containing exactly {CORRECT_INDICES_COUNT} integer in range [0, 3]

Example (return an array exactly like this):
[
  {{
    "question_type": "multiple_choice",
    "question": "What is the capital of France?",
    "options": ["Berlin", "Madrid", "Paris", "Rome"],
    "correct_indices": [2],
    "explanation": "Paris has been the capital of France since the 12th century."
  }}
]
"""


class MultipleChoiceQuestion(SingleAnswerQuestion):
    question_type: Literal["multiple_choice"]
    expected_options_count: ClassVar[int] = MULTIPLE_CHOICE_OPTIONS_COUNT
    system_prompt: ClassVar[str] = (
        f"{BaseQuestion.base_system_prompt}\n\n{_MULTIPLE_CHOICE_SYSTEM_PROMPT_SUFFIX.strip()}\n"
    )


class TrueFalseQuestion(SingleAnswerQuestion):
    question_type: Literal["true_false"]
    expected_options_count: ClassVar[int] = TRUE_FALSE_OPTIONS_COUNT


class MultiSelectQuestion(OptionsQuestion):
    question_type: Literal["multi_select"]

    @field_validator("options")
    @classmethod
    def minimum_options_count(cls, v: list[str]) -> list[str]:
        if len(v) < MIN_OPTIONS_COUNT:
            raise ValueError(f"{cls.__name__} requires at least {MIN_OPTIONS_COUNT} options")
        return v

    @field_validator("correct_indices")
    @classmethod
    def minimum_correct_indices(cls, v: list[int]) -> list[int]:
        if len(v) < MIN_CORRECT_INDICES_COUNT:
            raise ValueError(f"{cls.__name__} correct_indices must have at least {MIN_CORRECT_INDICES_COUNT} element")
        return v


class ShortAnswerQuestion(BaseQuestion):
    question_type: Literal["short_answer"]
    expected_answer: str


QuizQuestion = Annotated[
    Union[
        MultipleChoiceQuestion,
        TrueFalseQuestion,
        MultiSelectQuestion,
        ShortAnswerQuestion,
    ],
    Field(discriminator="question_type"),
]


class QuizSchema(BaseModel):
    questions: list[QuizQuestion]


class QuizResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    questions: list[QuizQuestion]
    model_used: str
    source: Literal["topic", "file"]
    truncated: bool = False
