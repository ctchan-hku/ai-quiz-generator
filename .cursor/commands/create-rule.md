---
description: Use when creating a Cursor rule to ensure it follows the project's format — situation-aimed description, PREFIX-NN body headings, pseudocode examples, self-contained sections.
---

# Create Rule

Follow the base `/create-rule` workflow, then apply the additional requirements below.

---

## Rule File Structure

```
---
description: >
  Use when <situation> to ensure <aim>.
globs:
  - "<pattern>"
alwaysApply: false
---

# Title

## PREFIX-01 — First requirement

## PREFIX-02 — Second requirement
```

---

## Description Field

State a **situation or trigger** followed by an **aim** — not an exhaustive list of topics covered. Two sentences maximum.

---

## Body — ID Headings

Every normative item must use a level-2 heading with an ID (`## PREFIX-NN — Title`). Choose a prefix that signals the *kind* of norm:

- `EXEC` — sequential steps or workflow actions
- `PROH` — things explicitly forbidden
- `STRUCT` — structural or organisational constraints
- `API` — interface or contract-level conventions

Number from `01` with no gaps. Renumber after any insertion or deletion. One heading per requirement.

---

## Body — Examples

All code examples must be language-agnostic pseudocode — plain English identifiers, indentation, and `//` comments. Label every pair `// bad` / `// good`.

---

## Body — Self-Contained Sections

Each section must stand alone:

- Do not reference other `.mdc` files or shared glossaries.
- If the same idea appears elsewhere, merge the sections rather than duplicating wording.
