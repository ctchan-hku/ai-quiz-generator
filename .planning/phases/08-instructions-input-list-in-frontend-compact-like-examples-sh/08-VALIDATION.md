# Phase 8 — Validation

**Derived from:** [08-RESEARCH.md](08-RESEARCH.md) “Validation architecture”

| Check | How |
|-------|-----|
| Normalizer | `pytest` on `normalize_user_instructions` / `USER_INSTRUCTIONS_ADDON.normalize` — empty, trim, max lines, max chars → 422 |
| API | Manual or test: generate with/without `user_instructions`; malformed body 422 |
| Frontend | `npx tsc --noEmit`; submit with rows → payload includes array; omit when empty |
| LLM contract | `outline()` still contains `json`; merged block is third segment only |
