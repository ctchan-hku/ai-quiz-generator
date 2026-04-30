# Milestones

## v1.1 Generation quality & control (Shipped: 2026-04-30)

**Phases completed:** 4 phases (6–9), 7 plans

**Key accomplishments:**

- Few-shot / style examples on **`POST /api/generate/quiz`** and **gpt-4.1** in the catalog with QuizForm UX.
- **`POST /api/generate/question`** per-MCQ refinement with shared rate limit, client version stacks, export from selected revisions.
- Optional **`user_instructions`** merged into **`FullQuizLlm`** system constraints before few-shot appendix.
- Reasoning-first MCQ prompt contract (**`MULTIPLE_CHOICE_CONSTRAINTS`**, **`MCQ_CHAIN_OF_THOUGHT`**), topic-vs-examples user emphasis, **post-parse option shuffle** for full quiz and single MCQ.

**Artifacts:** [milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) · [milestones/v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md)

**Note:** No dedicated `v1.1-MILESTONE-AUDIT.md`; closure followed **`audit-open`** (clear) and full REQ traceability for Phases 6–9.

---
