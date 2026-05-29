from fastapi import HTTPException

SECTION_LIST_ENTRY_TOO_LONG_DETAIL = (
    "Each list entry exceeds the maximum allowed length (after trim)"
)

SECTION_LIST_TOO_MANY_ENTRIES_DETAIL = "Too many list entries"


class SectionFormatter:
    __slots__ = ("_max_items", "_max_line_chars", "_intro")

    def __init__(self, max_items: int, max_line_chars: int, intro: str = "") -> None:
        self._max_items = max_items
        self._max_line_chars = max_line_chars
        self._intro = intro

    def normalize(self, raw: list[str] | None) -> list[str]:
        if raw is None:
            return []
        out: list[str] = []
        for s in raw:
            t = s.strip()
            if not t:
                continue
            if len(t) > self._max_line_chars:
                raise HTTPException(
                    status_code=422,
                    detail=SECTION_LIST_ENTRY_TOO_LONG_DETAIL,
                )
            out.append(t)
        if len(out) > self._max_items:
            raise HTTPException(
                status_code=422,
                detail=SECTION_LIST_TOO_MANY_ENTRIES_DETAIL,
            )
        return out

    def format_section(self, lines: list[str]) -> str:
        if not lines:
            return ""
        blocks: list[str] = []
        if self._intro:
            blocks.append(self._intro)
        for i, text in enumerate(lines, start=1):
            blocks.append(f"{i}. {text}")
        return "\n".join(blocks)
