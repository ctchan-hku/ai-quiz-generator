# Phase 7: Per-question regeneration — Context

**Gathered:** 2026-04-27  
**Updated:** 2026-04-27 — *single-question body, `/api/generate/question`, no sibling context, one `comment` field*  
**Mode:** `/gsd-discuss-phase 7 --batch` (gray areas resolved from v1.1 requirements + existing code; no interactive pick)  
**Status:** Ready for planning

<domain>
## Phase Boundary

**In scope (v1.1 Phase 7):**

- New **`POST /api/generate/question`** (same URL shape as **`POST /api/generate/text`**) returning one validated **`MultipleChoiceQuestion`** (AI-RG-01…05)
- `json_object` LLM call, one corrective retry, then **502** (same spirit as `parse_with_retry`)
- **Rate limit** shared intent with full-quiz generate (AI-RG-04) — do not allow **6**/hour by calling both endpoints
- **Review UI:** per-question **Regenerate/Refine** with **Confirm** / **Cancel**; client sends the **current version** of that slot’s MCQ + optional **comment** only (**FE-RG-01**…**FE-RG-04**)
- **Version history (client-only):** each question slot stores **all** `MultipleChoiceQuestion` snapshots produced by initial generate and each regen; the user **selects** which version is active for display, further refinement, and export (**D-7-16**…**D-7-20**)
- **No sibling context:** the model improves **only** from **topic** + the **submitted `question`** + **`comment`**. Other quiz items are not sent to the server for this call.
- `useQuizMachine` (or equivalent) can **append a version** and **change selected version** without clobbering other slots

**Out of scope:**

- Document upload, new question **types** beyond `multiple_choice`, batch regen of the whole quiz
- Changing quiz-level `model_used` or `source` on regen (see **D-7-15**)
- **Server-side** persistence of version history (history lives in **SPA state**; refresh loses prior versions — document in UAT)
- `localStorage` of regen history *(versions still session-only unless a later phase adds storage)*

**Depends on:** Phase 6 (few-shot + catalog) — *complete.*

</domain>

<decisions>
## Implementation Decisions

### API shape (AI-RG-01, AI-RG-02)

- **D-7-01:** Path **`POST /api/generate/question`** on the same router as **`POST /api/generate/text`** (pattern **`/api/generate/<segment>`**). Full path: **`/api/generate/question`**.
- **D-7-02:** Pydantic body: `model: str`, `topic: str` (1…2000), **`question: MultipleChoiceQuestion`** — the **current version** of the MCQ to improve (entire object in the request); **`comment: str | None = None`** (optional, **max 2_000** after trim) — the only free-text user feedback; if empty, server uses the neutral default from **D-7-04**. **No** `questions` array, **no** `question_index`, **no** `instruction` field, **no** sibling payload. **Response** JSON: **`{ "question": <MultipleChoiceQuestion> }`** (AI-RG-02).
- **D-7-03:** Reject with **422** if: `model` not in `settings.available_model_ids`; `question` fails `MultipleChoiceQuestion` validation; or `comment` over length after trim. Match existing generate error tone where practical.

### Comment and neutral default (AI-RG-01, product)

- **D-7-04:** If **`comment` is** missing, null, or **empty after trim**, the user message must still include the **fixed neutral** “rewrite this question” style hint (concrete string in PLAN/implementation). If **`comment` is non-empty**, include a single **“Editor comment:”** (or equivalent) block with the comment text. **One** feedback channel only.

### LLM — messages and output (AI-RG-03, AI-RG-05)

- **D-7-05:** **Response format:** `response_format={"type": "json_object"}`. The model must return **one** JSON object that **directly** validates as **`MultipleChoiceQuestion`** (not `{ "questions": [ … ] }` and not a bare array) — add a **dedicated** system prompt + one **new** `parse_single_mcq_with_retry` (or equivalent name) in `app/services/parser.py` that mirrors `parse_with_retry`’s *two-step* flow (one assistant failure → corrective user message → second completion) but validates **`MultipleChoiceQuestion`** only, then on second failure **502** (AI-RG-05).
- **D-7-06:** **User** message should include, in order: quiz **topic**; the **target** `question` (all fields) as structured text; then **editor comment** or neutral default per **D-7-04**. **Do not** include other questions from the quiz, stems-only or otherwise.
- **D-7-07:** **Do not** include few-shot from the original generate in this call (out of scope for v1.1 P7).
- **D-7-08:** `CHAT_COMPLETION_KWARGS` in `llm.py` (temperature, `max_tokens` budget) can be **reused**; set **`max_tokens`** in PLAN to a value appropriate for **one** MCQ if the default 4096 is wasteful (planner’s call).

### Rate limiting (AI-RG-04)

- **D-7-09:** The new route must use **`@limiter.shared_limit("3/hour", scope=...)`** with **`POST /api/generate/text`** (same `scope` string) so **one** 3/hour bucket per IP across **text + question** (replace plain `@limiter.limit` on `generate_text` when implementing). Document in README.

### Frontend — model source (FE-RG-02)

- **D-7-10:** Regeneration request uses the **currently selected form model** from **`App`**: the same `resolvedModel` / picker used for **`generateQuiz`**. `quiz.model_used` stays the **first** full-quiz generate’s model.
- **D-7-11:** Pass **`topic` from `App` state** with the call — the same string passed to `QuizDisplay`.

### Frontend — UX (FE-RG-01, FE-RG-03)

- **D-7-12:** **Inline** expand: each question card gets **Regenerate/Refine** with **Confirm** / **Cancel**; **Confirm** calls the API with **`question`** = **resolved** `MultipleChoiceQuestion` for that index and **`comment`** = that slot’s review textarea. **No** separate instruction field in UI. **No** new UI library.
- **D-7-13:** **Loading:** per-question `regeneratingIndex` (or equivalent) so other cards stay interactive (FE-RG-03). **Errors** per index; never drop the whole quiz.
- **D-7-16:** On success, **append** the returned `MultipleChoiceQuestion` to that slot’s **version list** and set **selected version** to the **new** one. **Do not** discard prior versions.
- **D-7-17:** **Client data model:** For each index `i`, keep **`versions[i]: MultipleChoiceQuestion[]`** (non-empty) and **`selectedVersionIndex[i]: number`**. Initialize on full-quiz success: one version per index; **refine** = `append` to `versions[i]`, `selected = last`.
- **D-7-18:** **Version selector UI:** On each question card, top area — **`<select>`** for **Version 1 … N**. Changing selection updates **`selectedVersionIndex[i]`**; **default: reset** reveal when switching version.
- **D-7-19:** **Comments** array stays **per question index** (not per version). **Default:** do **not** clear comment after a successful regen.

### Exports and journal (FE-RG-04)

- **D-7-15:** **Export** and journal use a **synthetic** `QuizResponse` where **`questions[i]`** is **`versions[i][selectedVersionIndex[i]]`**. **Comments** in export stay the parallel `comments[]`.
- **D-7-20:** `CurrentQuizActions` / export builders receive a **resolved** `QuizResponse` from App — on-screen questions = export.

### Claude’s discretion

- Exact “Version 1/2” labels; exact neutral-rewrite + “Editor comment:” copy in prompts.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/REQUIREMENTS.md` — AI-RG-01…05, FE-RG-01…07
- `.planning/ROADMAP.md` — Phase 7 success criteria
- `.planning/STATE.md` — current focus
- `.planning/phases/02-ai-generation-pipeline/02-CONTEXT.md` — rate limit note (D-01 message)
- `.planning/phases/06-few-shot-math-model/06-CONTEXT.md` — `generate` + `parse_with_retry` / few-shot patterns
- `backend/app/models/schemas.py` — `QuizQuestion`, `MultipleChoiceQuestion`, `QuizResponse`
- `backend/app/routers/generate.py` — `GenerateTextRequest`, model 422, `limiter`
- `backend/app/services/llm.py` — `CHAT_COMPLETION_KWARGS`, `get_llm_client`
- `backend/app/services/parser.py` — `parse_with_retry` pattern
- `frontend/src/hooks/useQuizMachine.ts` — reducer, `GENERATE_*` actions
- `frontend/src/components/QuizDisplay.tsx` — question cards, `CurrentQuizActions`
- `frontend/src/App.tsx` — `topic`, `resolvedModel`, `state.quiz` wiring

</canonical_refs>

<code_context>
## Existing Code Insights

### Reuse

- `get_llm_client`, `CHAT_COMPLETION_KWARGS` (adjust `max_tokens` if needed for one MCQ)
- Pydantic `MultipleChoiceQuestion` and `parse_with_retry` *pattern*; new **single-question** parser entry point
- `settings.available_model_ids` for 422
- `slowapi` `limiter` in `app/limiter.py` — must align with **D-7-09**

### Integration

- New route alongside `POST /api/generate/text` in `routers/generate.py` (or split module included from `main.py`)
- Frontend: new API in `lib/api.ts`, types in `types/api.ts` / `quiz.ts`
- `QuizFormConfig.model` and `App`’s `topic` available when `state.status === 'reviewing'`

</code_context>

<specifics>
## Specific Ideas

- **Reducer actions (sketch):** `APPEND_QUESTION_VERSION: { index, question }`, `SET_QUESTION_VERSION: { index, selected }`, init from `GENERATE_SUCCESS` to seed **versions** / **selected**; only in `reviewing` (default).
- **Tests:** Pydantic validation on request/response; unit test for `build_improve_messages` (topic + question + comment / neutral) — no sibling lines.

</specifics>

<deferred>
## Deferred Ideas

- Modal dialog for regen, per-question model dropdown, “regen all”, few-shot in regen
- **Sibling / cross-question** context in the LLM (intentionally out of scope for v1.1)
- Stamping `model_used` per question
- **Persistence** of version stacks across page reload (`localStorage` / server)
- Per-**version** comments (one comment per slot remains the product for v1.1)

</deferred>

---

*Phase: 07 — Per-question regeneration (v1.1)*  
*Context gathered: 2026-04-27*
