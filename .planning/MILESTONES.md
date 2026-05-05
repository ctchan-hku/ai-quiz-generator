# Milestones

## v1.2 Model board & generation cost visibility (Shipped: 2026-05-05)

**Phases completed:** 2 phases (10–11), 4 plans

**Key accomplishments:**

- **`GET /api/models`** exposes **`price.input` / `price.output`** (USD/M) merged from env catalog and reference JSON; **`app.state.models_catalog`** at startup.
- **`POST /api/generate/quiz`** and **`POST /api/generate/question`** return **`cost_usd`** from provider usage and configured rates (including retry completions).
- **Model board** replaces dropdown: cards, **price sort** asc/desc, **Pricing unavailable** when rates missing.
- **Stop** aborts full-quiz and refine (**`AbortController`**); **`GENERATE_ABORTED`** path avoids bogus error on user cancel.
- **Cost** on review header, **clipboard** export line, **export journal** schema v2; **`formatEstimatedCostUsd`**.
- **Backend:** **`cancel_on_client_disconnect`** on generate routes (HTTP **499** when client drops).

**Artifacts:** [milestones/v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md) · [milestones/v1.2-REQUIREMENTS.md](milestones/v1.2-REQUIREMENTS.md)

**Note:** No `v1.2-MILESTONE-AUDIT.md`. Pre-close **`audit-open`** — all clear (2026-05-05). Requirements traceability 10/10; **UAT** phases 10–11 marked complete.

---

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
