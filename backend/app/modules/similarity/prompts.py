def format_embeddable_question(*, prompt: str, options: list[str]) -> str:
    stem = prompt.strip()
    if not stem:
        return ""

    lines = [stem, "Options:"]
    for option in options:
        label = option.strip()
        if label:
            lines.append(f"- {label}")
    return "\n".join(lines)
