# Phase 6: Few-shot examples + math model — Context

**Gathered:** 2026-04-27  
**Mode:** `/gsd-discuss-phase 6 --batch` (all gray areas resolved from v1.1 requirements + codebase; no interactive area pick)  
**Status:** **Delivered** (2026-04-27) — plans executed; see `06-UAT.md`

<domain>
## Phase Boundary

Extend **topic-only** full-quiz generation so users can optionally attach up to **three** style/example strings that are injected into the **system** message; add **`gpt-4.1`** to the default model catalog and documentation.

**In scope (v1.1 Phase 6):**

- `POST /api/generate/text`: optional `few_shot_examples` (MOD-01/02, AI-FS-01…04, FE-FS-01…03, DEPLOY-04)
- `llm.build_messages` / `generate_quiz`: accept normalized example list; append few-shot block per **AI-FS-02**
- `app/config.py` `_FALLBACK_MODELS` + `backend/.env.example` + README for **gpt-4.1**
- Frontend: types, `generateQuiz` body, `QuizForm` UI (collapsible examples), `QuizFormConfig` + machine payload if needed

**Out of scope (deferred):**

- Per-question regeneration (**Phase 7**)
- Server-side persistence of presets
- Document upload

</domain>

<decisions>
## Implementation Decisions

### Model catalog (MOD-01, MOD-02, DEPLOY-04)

- **D-6-01:** Append **`{"id": "gpt-4.1", "label": "GPT-4.1 (math & reasoning)"}`** to `_FALLBACK_MODELS` after the existing two entries (order: `gpt-4o-mini`, `gpt-4o`, `gpt-4.1`).
- **D-6-02:** Document in README and `backend/.env.example` that operators must confirm the literal **`gpt-4.1`** string with their OpenAI-compatible provider; if the proxy uses a different id, only the JSON env / fallback list changes — no code branch per provider.

### Request validation (AI-FS-01)

- **D-6-03:** Field name **`few_shot_examples`**, type **`list[str]`**, optional on the Pydantic model (omit or `null` = not present).
- **D-6-04:** **Max 3** entries **after normalization**: trim each string; **drop** entries that are empty after trim; if the list is empty after normalization, treat as **no few-shot block** (same as omission). Reject with **422** if more than 3 non-empty examples remain.
- **D-6-05:** Each non-empty example **max length 2000** characters (post-trim); align frontend `maxLength` and shared constant or duplicated literal with comment pointing to backend.

### Prompt injection (AI-FS-02, AI-FS-03)

- **D-6-06:** Few-shot block is appended to the **system** message **after** the concatenation of `SYSTEM_PROMPT_HEADER` and `MultipleChoiceQuestion.system_prompt` (today: `f"{SYSTEM_PROMPT_HEADER}\n\n{question_class.system_prompt}"` — keep that base, then append `\n\n` + few-shot section).
- **D-6-07:** Section content (implementer may tighten wording): introduce that the following are **user-authored examples** for **tone, difficulty, and format**; output must still be only the required JSON; **do not copy** example text verbatim into the quiz; numbered **Example 1 / 2 / 3** with quoted or clearly delimited verbatim user strings.
- **D-6-08:** Pass the **same** `messages` list from the initial completion into `parse_with_retry` so retries keep the few-shot block (**AI-FS-03**). Signature change: `build_messages(..., few_shot_examples: list[str] | None = None)` and `generate_quiz(..., few_shot_examples: list[str] | None = None)` (or equivalent narrow type after router normalization).

### Frontend (FE-FS-01…03)

- **D-6-09:** Optional examples live under a **`<details>`** (“Example / style hints” or similar). **Initially there are zero** example fields. An **Add example** control appends a new row (up to **3** rows); each row is a `<textarea>` plus a **Remove** control that deletes that row only. Disable or hide **Add** when the count is **3**. Map row order to `few_shot_examples` indices after normalization (trim, drop empty).
- **D-6-10:** Examples live in **React state** on the form (or parent holding form state); **no** `localStorage` for v1.1.
- **D-6-11:** When the normalized list is non-empty, include **`few_shot_examples`** on **`QuizFormConfig`** and in the JSON body to **`generateQuiz`**; when empty, **omit the property** entirely (do not send `null` or `[]` unless OpenAPI/docs require — default **omit** for minimal payloads). Backend still treats `[]` like omission if ever sent.
- **D-6-12:** Loading and error UX unchanged except validation messages for too-long / too-many examples if enforced client-side.

### Verification (AI-FS-04)

- **D-6-13:** Phase UAT documents **one** run with examples and **one** without, noting observable difference (tone/structure spot-check); automated test optional if already heavy — preference **document in UAT** at minimum.

### Claude’s discretion

- Exact subsection title for the few-shot block; minor prompt wording; formatting of the default `AVAILABLE_MODELS` line in `.env.example`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning

- `.planning/PROJECT.md` — stack, constraints
- `.planning/REQUIREMENTS.md` — MOD-01/02, AI-FS-01…04, FE-FS-01…03, DEPLOY-04
- `.planning/ROADMAP.md` — Phase 6 success criteria
- `.planning/STATE.md` — current focus

### Prior phase context

- `.planning/phases/02-ai-generation-pipeline/02-CONTEXT.md` — generation pipeline, rate limit note
- `.planning/phases/03-react-frontend-topic-flow/03-UI-SPEC.md` — UI patterns (if still authoritative)

### Architecture

- `.planning/research/ARCHITECTURE.md` — API and prompt notes where still accurate

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- `backend/app/services/llm.py` — `SYSTEM_PROMPT_HEADER`, `build_messages`, `generate_quiz`, `CHAT_COMPLETION_KWARGS`
- `backend/app/routers/generate.py` — `GenerateTextRequest`, `generate_text`, model allowlist **422**
- `backend/app/config.py` — `_FALLBACK_MODELS`, `available_models` / `available_model_ids`
- `backend/app/services/parser.py` — `parse_with_retry(raw, client, messages, ...)`
- `frontend/src/lib/api.ts` — `generateQuiz` builds `GenerateTextRequest`
- `frontend/src/types/api.ts` — request types
- `frontend/src/components/QuizForm.tsx` — topic, count, model, submit → `QuizFormConfig`
- `frontend/src/types/quiz-machine.ts` — `QuizFormConfig`, `START_GENERATE`
- `frontend/src/config/quiz.ts` — topic max length 2000 (mirror for few-shot max per **D-6-05**)

### Integration points

- Extend `GenerateTextRequest` (Python + TS) and thread through `generate_quiz` → `build_messages`.
- `GET /api/models` needs no code change if it already reflects `settings.available_models` after config update.

### Established patterns

- Unknown model → **422** with sorted valid ids list.
- `json_object` completion and retry path already depend on stable `messages`.

</code_context>

<specifics>
## Specific Ideas

- Normalization helper (backend): one function `normalize_few_shot_examples(raw: list[str] | None) -> list[str]` returning 0–3 trimmed non-empty strings or raises `HTTPException(422)` — keeps router thin.
- Frontend: `FEW_SHOT_MAX_COUNT = 3` and `FEW_SHOT_MAX_LENGTH = 2000` in `config/quiz.ts` next to topic limit; reuse for Add-button cap and `maxLength`.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 7:** `POST /api/generate/question` (topic + target `question` + optional `comment`); form model for refine (**REQUIREMENTS.md** / **07-CONTEXT**).
- Three fixed always-visible textareas (replaced by **D-6-09** add/remove pattern).
- Server-stored example presets.

</deferred>

---

*Phase: 06 — Few-shot + math model (v1.1)*  
*Context gathered: 2026-04-27*
