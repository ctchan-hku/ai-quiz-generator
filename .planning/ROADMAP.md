# Roadmap — AI Quiz Generator

**Last updated:** 2026-05-05  
**Active planning:** **v1.3 — Layered system architecture** (Phases 12–15).  
**Reference:** [docs/system-flow](../docs/system-flow) · [.planning/REQUIREMENTS.md](REQUIREMENTS.md)

---

## Milestones

| Version | Name | Phases | Artifacts |
|--------|------|--------|-----------|
| v1.0 | MVP | 1–5 | [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) |
| v1.1 | Generation quality & control | 6–9 | [v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) · [v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md) |
| v1.2 | Model board & cost visibility | 10–11 | [v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md) · [v1.2-REQUIREMENTS.md](milestones/v1.2-REQUIREMENTS.md) |
| **v1.3** | **Layered system architecture** | **12–15** | [REQUIREMENTS.md](REQUIREMENTS.md) (this milestone) |

---

## Phases (v1.3)

Numbering continues after v1.2 (**Phase 11** complete → **Phase 12** starts v1.3).

- [ ] **Phase 12 — Past paper pipeline (data layer)** — Teacher upload of past papers (PDF-first); parse text, segment questions, classify types, extract MCQ/short-answer fields, tag metadata (e.g. course ID), return structured quiz JSON (**ARCH-01**, **ARCH-02**, **DATA-01**, **DATA-02**, **DATA-03**).

- [ ] **Phase 13 — Generation layer** — Optional structured spec on generate APIs; retrieval-before-LLM when index has data; validator pipeline + `generation_debug` (**GEN-01**, **GEN-02**, **GEN-03**, **GEN-04**).

- [ ] **Phase 14 — Review layer** — UI pipeline summary; per-question disposition + reason in export paths (**REV-01**, **REV-02**).

- [ ] **Phase 15 — Deployment layer** — Publish bundle export; structured stage logging with correlation id (**DEP-01**, **DEP-02**).

---

### Phase details

#### Phase 12: Past paper pipeline (data layer)

**Goal:** Deliver the **past paper** slice of the data layer: teachers upload past papers (primarily PDF); the system extracts text, segments items using question-boundary detection, classifies each item’s type, extracts structured fields for **MCQ** and **short-answer** items, attaches metadata (e.g. **course ID**), and returns a **structured quiz JSON** that later layers can consume—aligned with [docs/system-flow](../docs/system-flow).

**Depends on:** v1.2 complete  

**Requirements:** ARCH-01, ARCH-02, DATA-01, DATA-02, DATA-03  

**Success criteria:**

1. Teachers can upload a past paper through the intended route; **PDF** is the primary supported format, with a documented behavior for parse or validation failures.
2. The pipeline produces segmented questions from the source document (boundary detection); empty or ambiguous segments surface as structured errors or warnings rather than silent drops.
3. Each segmented item has a **question type**; for **MCQ** and **short-answer**, required fields are extracted into shared types or a documented JSON schema.
4. Output includes **paper-level metadata** (at least **course ID** where provided) plus the full quiz payload as **structured JSON** suitable for generation/review layers.
5. **ARCH-01** / **ARCH-02** remain satisfied: layer boundaries and repo mapping stay documented as this pipeline lands.

#### Phase 13: Generation layer

**Goal:** Implement the **generation layer** slice: structured optional spec, retrieval hook, validators, debug payload—without regressing topic-only quiz generation.

**Depends on:** Phase 12  

**Requirements:** GEN-01, GEN-02, GEN-03, GEN-04  

**Success criteria:**

1. Existing topic-only `POST /api/generate/quiz` (and question refine) still succeed when new optional fields are absent.
2. When fixture content is loaded and spec targets it, retrieval supplies grounding snippets to the prompt path (verified by test or logged trace).
3. Invalid LLM output fails validation with actionable structure before returning to client.
4. Successful responses include `generation_debug` (or equivalent) for UI consumption.

#### Phase 14: Review layer

**Goal:** Expose **review layer** affordances: transparency into spec/retrieval/validation and instructor-style disposition on each item.

**Depends on:** Phase 13  

**Requirements:** REV-01, REV-02  

**Success criteria:**

1. Review UI shows pipeline summary when data exists; empty state is graceful for legacy flows.
2. Export clipboard and journal include disposition and optional reason per question when user set them.

#### Phase 15: Deployment layer

**Goal:** Close the loop with **deployment-oriented** export and operability—preparing for future LMS handoff and continuous learning without implementing LMS.

**Depends on:** Phase 14  

**Requirements:** DEP-01, DEP-02  

**Success criteria:**

1. User can download or export a **publish bundle** JSON that includes quiz content plus layer metadata defined in **DEP-01**.
2. Server logs (or structured log lines) allow correlating one generate request across retrieve/validate/llm stages.

---

## Progress (v1.3)

| Phase | Status | Target |
|-------|--------|--------|
| 12. Past paper pipeline (data layer) | Not started | v1.3 |
| 13. Generation layer | Not started | v1.3 |
| 14. Review layer | Not started | v1.3 |
| 15. Deployment layer | Not started | v1.3 |

---

<details>
<summary>✅ v1.2 — Model board & cost (Phases 10–11) — SHIPPED 2026-05-05</summary>

- [x] **Phase 10** — Models API pricing + **`cost_usd`** on generate endpoints (plans 10-01, 10-02).
- [x] **Phase 11** — Model board, price sort, Stop/abort, cost in UI + journal/clipboard (plans 11-01, 11-02).

Full detail: [milestones/v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md).

</details>
