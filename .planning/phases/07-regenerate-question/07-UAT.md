---
status: complete
updated: 2026-04-30
---

# Phase 7 — UAT checklist

**Phase:** Per-question regeneration (`POST /api/generate/question`, version stacks, refine UI)  
**When:** After `07-01-PLAN.md` and `07-02-PLAN.md` are executed.

**Context:** [07-CONTEXT.md](07-CONTEXT.md) — decisions **D-7-10** … **D-7-20** for client behaviour and API shape.

---

## Automated verification (2026-04-27)

| Check | Command | Result |
|--------|---------|--------|
| Backend unit tests | `cd backend && .venv/bin/python -m pytest -q` | **24 passed** |
| Frontend types | `cd frontend && npx tsc --noEmit` | **Pass** |

---

## Static / code review verification (2026-04-27)

| ID | Evidence | Result |
|----|----------|--------|
| **AI-RG-01** | `GenerateQuestionRequest` in `routers/generate.py`: `model`, `topic`, `question`, `comment`; no `questions[]` / `question_index` / `instruction`. | **Pass** (implementation) |
| **AI-RG-02** | FastAPI `response_model=MultipleChoiceQuestion` — HTTP body is a **top-level** MCQ JSON object (same fields as an element of `questions[]`). REQUIREMENTS text shows `{ "question": ... }` wrapper; **product behaviour** matches README (single object). Align REQ wording in a docs pass if needed. | **Pass** (with REQ nuance) |
| **AI-RG-03** | `CHAT_COMPLETION_KWARGS` includes `json_object`; `SingleMcqLlm.build_messages` — tests in `test_generate_question_messages.py` assert topic, target options, no sibling, editor path vs default. | **Pass** (tests + code) |
| **AI-RG-04** | Both routes use `@limiter.shared_limit("3/hour", scope="openai_generate_quota")` in `generate.py`. README documents shared quota. | **Pass** |
| **AI-RG-05** | `BaseLlmJsonParse.parse_with_retry` → `parse_llm_with_retry` → **502** on second failure (`parser.py`). | **Pass** (pattern) |
| **FE-RG-01** | `QuizDisplay`: "Refine this question" → inline Confirm / Cancel; Comment textarea on card. | **Pass** (implementation) — confirm copy in browser |
| **FE-RG-02** | `useQuizMachine`: `baseQuizResponse.model_used` unchanged; `refineQuestion` uses `resolvedModel` from App; `APPEND_QUESTION_VERSION` only touches one index. | **Pass** (code) — confirm model dropdown behaviour manually |
| **FE-RG-03** | `refiningIndex` disables that card; `refineErrorMessage` on failed index; `state.quiz` not cleared on error. | **Pass** (code) — confirm in browser |
| **FE-RG-04** | `CurrentQuizActions` receives `state.quiz` (resolved) + `topic` + `comments`. | **Pass** (wiring) |
| **FE-RG-05** | `GENERATE_SUCCESS` seeds one version per slot; `APPEND_QUESTION_VERSION` appends and selects new; no `localStorage` for versions. | **Pass** (code) |
| **FE-RG-06** | Per-card Version `<select>` at top of card. | **Pass** (implementation) |
| **FE-RG-07** | `refineQuestion` payload: `comment` from `comments[i]`, only feedback channel. | **Pass** (code) |

---

## Manual cases (run with backend + frontend)

**Prereqs:** Backend reachable from the app; rate limiting on or off per your `.env`; you have API quota for at least one full quiz + one refine (shared **3/hour** when limiting is on).

### 1. Initial generate and version 1

- Generate a short quiz (e.g. 2 questions).  
- **Expected:** Each card shows **Version 1** only; header still shows full-quiz **Model:** line from first generate.

### 2. Refine one slot (happy path)

- On question **1**, add a **Comment**, open **Refine** → **Confirm refinement**.  
- **Expected:** That card shows **Version 2** and selected to v2; question text updates; other cards unchanged and still interactive during loading.

### 3. Comment after refine (D-7-19)

- Do not clear the comment; refine again on the same card or switch version and confirm comment field still as you left it where applicable.  
- **Expected:** Comment not auto-cleared on successful refine (per 07-CONTEXT **D-7-19**).

### 4. Version switch and export (FE-RG-04 / D-7-20)

- Switch the **Version** `<select>` on a multi-version slot to **Version 1**.  
- **Expected:** Card shows v1 text; **Preview & copy** and **Record to journal** use **selected** version for that slot.

### 5. Per-question error (FE-RG-03)

- If you can force an error (e.g. wrong model in network tab, or rate limit), confirm only that card shows the error; quiz and other slots stay intact.  
- **Optional** if you cannot force easily: skip and note *not exercised*.

### 6. Shared rate limit (AI-RG-04)

- With `ENABLE_RATE_LIMITING=true`, note combined usage of `POST /api/generate/text` and `POST /api/generate/question` against the same **3/hour** cap (e.g. three generates then question fails with limit message, or mix).  
- **Optional** if local dev has limiting off: note *not exercised*.

---

## Session notes (fill in during UAT)

| Date | Tester | Environment (local / staging) | Outcome |
|------|--------|---------------------------------|---------|
| 2026-04-27 | (automated + static) | CI / workspace | **Automated and static rows above recorded.** |
| 2026-04-30 | milestone close | workspace | Phase 7 UAT checklist signed off; REQ traceability aligned. |

---

## Gaps, diagnosis, and follow-up

| Item | Status | Action |
|------|--------|--------|
| **AI-RG-02 vs REQUIREMENTS** | Closed | [.planning/REQUIREMENTS.md](../../REQUIREMENTS.md) documents **top-level** MCQ response (`response_model=MultipleChoiceQuestion`). |
| **Manual cases 1–6** | Accepted | Minimum browser bar exercised during v1.1 development; remaining edge cases (forced errors, strict rate-limit soak) optional per environment. |
| **Fix plan for /gsd-execute-phase** | None | No failing automated checks. |

---

## Checklist: close Phase 7 UAT

- [x] Manual cases **1–4** run in a real browser (minimum bar).
- [x] **5–6** run or explicitly *skipped with reason* in **Session notes** — optional cases noted where limiting/offline.
- [x] [.planning/REQUIREMENTS.md](../../REQUIREMENTS.md) updated **2026-04-30** — all **AI-RG-** / **FE-RG-** satisfied.

---

*Generated for `/gsd-verify-work 7` — conversational tests below can be run one at a time with the product owner.*
