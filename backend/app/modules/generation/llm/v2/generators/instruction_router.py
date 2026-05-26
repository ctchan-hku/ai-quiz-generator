from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.langchain.structured_step import StructuredLlmStep
from app.modules.generation.llm.v2.config.completion_tokens import (
    INSTRUCTION_ROUTER_TOKEN_BUDGET,
)
from app.modules.generation.llm.v2.config.prompt import (
    INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT,
    INSTRUCTION_ROUTER_ROLE_DEFAULT,
)


def _norm_key(text: str) -> str:
    return " ".join(text.strip().split()).casefold()


def _canonical_lookups(originals: list[str]) -> tuple[set[str], dict[str, str]]:
    exact = set(originals)
    norm_to_canonical: dict[str, str] = {}
    for line in originals:
        norm_to_canonical.setdefault(_norm_key(line), line)
    return exact, norm_to_canonical


def _resolve_line(
    fragment: str,
    *,
    exact: set[str],
    norm_to_canonical: dict[str, str],
) -> str | None:
    trimmed = fragment.strip()
    if not trimmed:
        return None
    if trimmed in exact:
        return trimmed
    return norm_to_canonical.get(_norm_key(trimmed))


def _populate_bucket(
    lines: list[str],
    *,
    exact: set[str],
    norm_to_canonical: dict[str, str],
) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in lines:
        if not isinstance(raw, str):
            continue
        canon = _resolve_line(raw, exact=exact, norm_to_canonical=norm_to_canonical)
        if canon is None or canon in seen:
            continue
        seen.add(canon)
        out.append(canon)
    return out


class RoutedInstructions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stem: list[str] = Field(default_factory=list)
    answer: list[str] = Field(default_factory=list)
    distractor: list[str] = Field(default_factory=list)


class InstructionRouterGenerator(StructuredLlmStep[RoutedInstructions]):
    parse_response_model: ClassVar[type[RoutedInstructions]] = RoutedInstructions

    def __init__(
        self,
        *,
        user_instructions: list[str],
    ) -> None:
        if not user_instructions:
            raise ValueError("user_instructions must be non-empty")
        self._instructions = list(user_instructions)

    @property
    def role_definition(self) -> str:
        return INSTRUCTION_ROUTER_ROLE_DEFAULT

    def completion_max_tokens(self) -> int:
        return INSTRUCTION_ROUTER_TOKEN_BUDGET.max_tokens(
            max(1, len(self._instructions)),
        )

    def structured_json_format(self) -> str:
        return (
            "{\n"
            '  "stem": ["...", "..."],\n'
            '  "answer": ["...", "..."],\n'
            '  "distractor": ["...", "..."]\n'
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        instructions_block = "\n".join(self._instructions)
        user_prompt = (
            "Task: Route each instruction line below into one or more of `stem`, `answer`, and "
            "`distractor`. An instruction belongs in multiple arrays when more than one stage must "
            "honor it (copy duplicates verbatim into each).\n\n"
            "Stem: wording, difficulty, realism, numerical setup, notation, formatting of the QUESTION ONLY.\n"
            "Answer: solving style, derivation depth, rounding, units, how the correct result "
            "and explanation are written.\n"
            "Distractor: how wrong choices are chosen, similarity to the truth, option counts.\n\n"
            "Rules:\n"
            "- Prefer copying each line EXACTLY as written.\n"
            "- Whitespace normalization is tolerated; wording must remain the same line (no rewriting).\n"
            '- Always include `"stem": [], "answer": [], "distractor": []` arrays (empty allowed).\n'
            "- Cover every line in at least one array when verbatim copies are feasible; "
            "otherwise place the ambiguous line conservatively across `stem`, `answer`, and `distractor` "
            "as needed.\n\n"
            f"Instructions to route:\n{instructions_block}"
        )
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    chain_of_thought=INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT,
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

    def post_process(self, routed: RoutedInstructions) -> RoutedInstructions:
        originals = self._instructions
        exact, norm_to_canonical = _canonical_lookups(originals)

        stem_out = _populate_bucket(
            routed.stem, exact=exact, norm_to_canonical=norm_to_canonical
        )
        answer_out = _populate_bucket(
            routed.answer, exact=exact, norm_to_canonical=norm_to_canonical
        )
        distr_out = _populate_bucket(
            routed.distractor, exact=exact, norm_to_canonical=norm_to_canonical
        )

        covered = set(stem_out) | set(answer_out) | set(distr_out)
        for req in originals:
            if req not in covered:
                stem_out.append(req)
                covered.add(req)

        return RoutedInstructions(
            stem=stem_out, answer=answer_out, distractor=distr_out
        )
