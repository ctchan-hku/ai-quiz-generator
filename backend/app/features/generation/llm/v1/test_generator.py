from typing import Any, ClassVar

from app.features.generation.helpers.options import shuffle_option_order
from app.features.generation.llm.shared.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.features.generation.llm.v1.test_generator_prompts import (
    TEST_AUTHOR_ROLE_DEFAULT,
    TEST_GENERATOR_FEW_SHOT_REMARK,
    TEST_GENERATOR_USER_PROMPT,
    TEST_SOURCE_PRIORITY_GUIDANCE,
    TOPIC_CONTEXT,
)
from app.features.generation.models import GeneratedTest, MultipleChoiceQuestion
from app.integrations.langchain.structured_step import StructuredLlmStep


class TestGenerator(StructuredLlmStep[GeneratedTest]):
    __test__ = False
    parse_response_model: ClassVar[type[GeneratedTest]] = GeneratedTest

    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
        user_instructions: list[str] | None = None,
    ) -> None:
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = few_shot_examples
        self._user_instructions = (
            user_instructions if user_instructions is not None else []
        )

    @property
    def role_definition(self) -> str:
        return TEST_AUTHOR_ROLE_DEFAULT

    def structured_json_format(self) -> str:
        n = self._num_questions
        qtype = self._question_class.QUESTION_TYPE_KEY
        return (
            "{\n"
            f'  "questions": [\n'
            "    {\n"
            f'      "question_type": "{qtype}",\n'
            '      "question": "...",\n'
            '      "options": ["...", "..."],\n'
            '      "correct_indices": [0],\n'
            '      "explanation": "..."\n'
            "    }\n"
            f"    ... exactly {n} question objects in this array ...\n"
            "  ]\n"
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        topic = self._topic.strip()
        context_blk = (
            TOPIC_CONTEXT.format(topic=topic)
            if topic
            else "The user did not provide a topic."
        )

        requirements_blk = getattr(self._question_class, "guardrails", "")
        if self._user_instructions:
            requirements_blk = (
                f"{requirements_blk}\n"
                f"{USER_INSTRUCTIONS_FORMATTER.format_section(self._user_instructions)}"
            )

        examples_blk = ""
        if self._few_shot_examples:
            examples_blk = FEW_SHOT_FORMATTER.format_section(self._few_shot_examples)

        chain_of_thought_blk = getattr(self._question_class, "chain_of_thought", "")

        system_prompt = self._system_prompt(
            guidelines=TEST_SOURCE_PRIORITY_GUIDANCE,
            context=context_blk,
            requirements=requirements_blk,
            examples=examples_blk,
            chain_of_thought=chain_of_thought_blk,
        )

        user_prompt = TEST_GENERATOR_USER_PROMPT.format(
            num_questions=self._num_questions,
            question_type=self._question_class.QUESTION_TYPE_KEY,
        )
        if self._few_shot_examples:
            user_prompt += TEST_GENERATOR_FEW_SHOT_REMARK

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def post_process(self, parsed: GeneratedTest) -> GeneratedTest:
        shuffled: list[MultipleChoiceQuestion] = []
        for q in parsed.questions:
            new_opts, new_ci = shuffle_option_order(
                list(q.options), list(q.correct_indices)
            )
            shuffled.append(
                q.model_copy(update={"options": new_opts, "correct_indices": new_ci})
            )
        return GeneratedTest(questions=shuffled)
