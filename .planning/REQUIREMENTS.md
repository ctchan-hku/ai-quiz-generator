# Requirements — v1.1 (generation quality & control)

**Version:** v1.1  
**Last updated:** 2026-04-27  
**Status:** Approved for implementation — Phase 6 **delivered**; Phase 7 pending  
**Builds on:** [v1.0 archive](milestones/v1.0-REQUIREMENTS.md)

---

## Theme

Improve quiz generation **quality and steerability**: optional **few-shot / style examples** in the system prompt, a **math-capable model** in the catalog, and **per-question refinement** via **`POST /api/generate/question`** with optional **comment** on the current MCQ.

---

## MOD — Model catalog

- [x] **MOD-01**: Default / documented model list includes **`gpt-4.1`** (exact upstream model ID) with a user-facing label that indicates stronger math/reasoning (e.g. “GPT-4.1 (math & reasoning)”). Implementation: extend `_FALLBACK_MODELS` in `app/config.py` and `.env.example` `AVAILABLE_MODELS`; Railway operators can override via `AVAILABLE_MODELS` JSON as today.
- [x] **MOD-02**: `GET /api/models` continues to expose only ids present in `settings.available_models`; `POST /api/generate/text` and regeneration endpoint reject unknown model ids with **422** (existing pattern).

---

## AI — Few-shot examples (full-quiz generation)

- [x] **AI-FS-01**: `POST /api/generate/text` accepts an optional **`few_shot_examples`** field: `list[str]`, **max 3** entries, each string **max 2_000** characters (aligned with topic cap order-of-magnitude). Empty list and omission behave identically (no few-shot block).
- [x] **AI-FS-02**: When non-empty, the backend injects a dedicated section into the **system** message (after `SYSTEM_PROMPT_HEADER` and the question-class instructions) that quotes the examples verbatim and instructs the model to **match tone, difficulty, and format** of the examples without copying them. Examples are **user-authored** (style / sample Q&A in prose or compact JSON-like text); no server-side template files required.
- [x] **AI-FS-03**: Few-shot content is included in the **initial** `messages` list passed to `parse_with_retry` so corrective retries remain consistent.
- [x] **AI-FS-04**: Integration test or manual UAT note: one run **with** and **without** examples documents observable difference (document in phase UAT).

---

## AI — Per-question regeneration

- [ ] **AI-RG-01**: New **`POST /api/generate/question`** (same path pattern as **`/api/generate/text`**) accepts JSON:
  - `model: str` (must be in `available_model_ids`)
  - `topic: str` (quiz topic for context)
  - `question: MultipleChoiceQuestion` — the **current version** of the MCQ to improve (full object in the body)
  - `comment: str` — optional review feedback (from UI); **max 2_000** characters after trim; if empty, server uses a neutral rewrite hint in the user message (`07-CONTEXT` **D-7-04**). **No** full-quiz array, **no** sibling context, **no** separate `instruction` field.
- [ ] **AI-RG-02**: Response body: `{ "question": <MultipleChoiceQuestion> }` validated with the same Pydantic model as full-quiz items.
- [ ] **AI-RG-03**: LLM call uses **json_object** mode and a **system** prompt that constrains output to one MCQ object; **user** message includes **topic**, the **target** `question` only, and **`comment`** / neutral default per **07-CONTEXT** **D-7-04** / **D-7-06** (no other questions from the quiz).
- [ ] **AI-RG-04**: **Rate limiting**: same **3 requests / IP / hour** bucket as `/api/generate/text` **or** a clearly documented stricter/limiter key shared across both (prefer one limiter scope so abuse cannot double throughput).
- [ ] **AI-RG-05**: On validation failure, **one** corrective retry (same pattern as `parse_with_retry`) then **502** if still invalid.

---

## FE — Few-shot UI

- [x] **FE-FS-01**: Quiz configuration surface exposes an optional **“Example / style hints”** control (collapsible `<details>` or secondary panel) with up to **3** text areas (or one textarea with clear delimiter instructions — UX choice in UI phase) mapped to `few_shot_examples[]`.
- [x] **FE-FS-02**: Examples are sent only on **Generate**; persisted in component state for the session (no requirement for `localStorage` in v1.1).
- [x] **FE-FS-03**: Loading/error behaviour unchanged aside from new optional field in `generateQuiz` request body.

---

## FE — Regenerate question UI

- [ ] **FE-RG-01**: On the quiz review screen, each question has a **Regenerate** / **Refine** control that opens a small flow (modal or inline expand) with **Confirm** / **Cancel** (review **Comment** textarea is on the card; optional copy can explain that Confirm sends it to improve the question).
- [ ] **FE-RG-02**: On success, **only** the targeted slot is updated: a **new version** of the question is **appended** (prior versions **preserved**); `model_used` on the parent quiz may remain the **original** generate model — **default:** keep quiz-level `model_used` as first generation model; regeneration uses **currently selected model** from the form. User can **switch active version** (see **FE-RG-05/06**).
- [ ] **FE-RG-03**: Disabled states: while regenerating, that question’s controls show loading; other questions remain interactive; failures show readable error (toast or inline) without discarding the whole quiz.
- [ ] **FE-RG-04**: Export/journal flows use the **currently selected** question text per slot (see **FE-RG-06**) without requiring a full re-generate.
- [ ] **FE-RG-05**: **Version history (client state):** each index `i` holds a non-empty list of `MultipleChoiceQuestion` and a **selected** index; initial generate creates **v1** only; each successful regen **appends** and selects the new version. History is **session-only** unless a later milestone adds persistence.
- [ ] **FE-RG-06**: A **version control** (e.g. `<select>`) appears at the **top area** of each question card (e.g. top-right) so the user can change which revision is **active** for display, further refinement, and export.
- [ ] **FE-RG-07**: The **Comment** field for a question is sent to **`POST /api/generate/question`** as **`comment`** and is the **only** free-text feedback field for refinement (see `07-CONTEXT` **D-7-04** / **D-7-12**).

---

## DEPLOY — Ops

- [x] **DEPLOY-04**: README and `.env.example` document new env shape for `AVAILABLE_MODELS` including **gpt-4.1** and remind operators to confirm the id with their **OpenAI-compatible provider** (openai-hk.com may use the same id as OpenAI; if not, ops edits JSON only).

---

## Out of scope (v1.1)

- Document **upload** track (still deferred; see v1.0 archive v2 section).
- **New question types** (TF / multi-select / short answer) in generation or regeneration — still **multiple_choice only**.
- **Batch** regeneration of the whole quiz in one call.
- Server-side **persistence** of user few-shot presets (browser-only / request-only is enough).

---

## Traceability

| Requirement | Phase (planned) | Notes |
|---------------|-----------------|-------|
| MOD-01, MOD-02 | Phase 6 ✓ | Config + docs |
| AI-FS-01 … AI-FS-04 | Phase 6 ✓ | `llm.py`, `generate.py`, parser wiring |
| AI-RG-01 … AI-RG-05 | Phase 7 | `POST /api/generate/question` + LLM + shared limiter + `question` + `comment` |
| FE-FS-01 … FE-FS-03 | Phase 6 ✓ | `QuizForm`, `api.ts`, types |
| FE-RG-01 … FE-RG-07 | Phase 7 | `QuizDisplay`, version state, export, regen + comment |
| DEPLOY-04 | Phase 6 ✓ | README / `.env.example` |

---

## Open choices (resolve in PLAN.md)

1. Regeneration **model** source: **resolved** — current form `model` (`07-CONTEXT` **D-7-11**).  
2. Few-shot UI: **resolved** (Phase 6) — add/remove rows.  
3. Sibling context in regeneration prompt: **resolved** — **not** sent; only **topic** + **target `question`** + **`comment`** (`07-CONTEXT` **D-7-06**).  
4. **Versions + comment-driven refine:** product locked in `07-CONTEXT` **D-7-16**…**D-7-20** and **FE-RG-05**…**FE-RG-07**.
