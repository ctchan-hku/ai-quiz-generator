def name_contains_excluded_term(
    name: str,
    excluded_terms: tuple[str, ...],
) -> bool:
    normalized_name = name.casefold()
    return any(term.casefold() in normalized_name for term in excluded_terms)
