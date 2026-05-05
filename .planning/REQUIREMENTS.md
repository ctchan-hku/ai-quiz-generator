# Requirements — AI Quiz Generator (v1.3)

**Defined:** 2026-05-05  
**Milestone:** v1.3 — Layered system architecture  
**Core value:** Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.  
**Architecture reference:** [docs/system-flow](../docs/system-flow) (data → generation → review → deployment).

---

## v1.3 Requirements

Scoped work for this milestone only. Numbering is per-category (`DATA-*`, `GEN-*`, `REV-*`, `DEP-*`, `ARCH-*`). **Topic-only flows remain default**; structured fields and retrieval are additive.

### ARCH — Architecture documentation & boundaries

- [x] **ARCH-01**: Published architecture description maps the **four layers** (data, generation, review, deployment) to **concrete repo locations** (packages, routers, UI areas) and links to [docs/system-flow](../docs/system-flow).
- [x] **ARCH-02**: Dependency rule is documented (e.g. data → generation → review → deployment; no upward imports from lower layers into higher layers) and reflected in how new code is organized.

### DATA — Data layer

- [ ] **DATA-01**: **Content unit** schema exists (id, text, metadata such as source label, optional `outcome_key`, `chunk_type`, `course_id` optional) as shared types usable by backend (and frontend where needed for display).
- [ ] **DATA-02**: **Content index** abstraction exists (e.g. register + query by keyword/simple filter) with a **memory-backed** implementation for development; no production DB required for v1.3.
- [ ] **DATA-03**: **Past paper ingest**: teachers can upload past papers (**PDF** primary); pipeline extracts text, detects **question boundaries**, infers **item type**, extracts fields for **MCQ** and **short-answer** items, attaches metadata (e.g. **`course_id`**), and returns a **structured quiz JSON** for downstream layers. A **fixture or dev path** may still exist to exercise the pipeline without a full UI where useful.

### GEN — Generation layer

- [ ] **GEN-01**: **Structured generation spec** extends existing quiz request: optional fields (e.g. `outcome_key`, `bloom_level`, `difficulty_target`, `constraints[]`) validated by Pydantic; **omitted fields** preserve current topic-only behavior.
- [ ] **GEN-02**: **Planning / retrieval** step runs before the LLM when the index has matching content: pluggable retriever returns **grounding snippets** (and empty list when index empty or no match).
- [ ] **GEN-03**: **Validator pipeline** interface exists; at least **schema/MCQ shape validation** and one **policy-style** check (e.g. forbidden patterns already in prompts) run on generated output before response; failures surface as structured errors or repair loop **without** breaking successful path tests.
- [ ] **GEN-04**: Generated quiz or items include **optional** `generation_debug` (or equivalent) payload: spec used, retrieval hit count, validator summary — omitted or trimmed in production via config if needed.

### REV — Review layer

- [ ] **REV-01**: Review UI shows a **pipeline summary** (collapsed/expandable): structured spec (if any), retrieval/validation summary from **GEN-04** (or client mirrors API fields).
- [ ] **REV-02**: Per question, user can set **disposition**: approved / rejected / needs-edit with **optional reason**; state is included in **clipboard** and **export journal** (schema bump if required, with backward compatibility or migration note).

### DEP — Deployment layer

- [ ] **DEP-01**: **Publish bundle** export (e.g. additional JSON download or journal variant) contains quiz MCQs plus **layer metadata** needed for a hypothetical LMS handoff: spec, disposition, timestamps, model/cost fields when present.
- [ ] **DEP-02**: **Structured logging** (or single request log record) for stages: `data_query`, `retrieve`, `validate`, `llm` — correlation id per generate request; documented in README for operators.

---

## Future requirements (deferred)

| Item | Note |
|------|------|
| Vector embeddings + ANN index | After document upload milestone |
| Secure item index & anti-duplication thresholding | Full system-flow Phase 1A |
| Misconception library + LMS stats loop | Phase 2+ of long-range plan |
| Human review queue with roles | Auth milestone |

---

## Out of scope (v1.3)

| Feature | Reason |
|---------|--------|
| Real LMS publish, student attempts, p-values | Requires integrations beyond MVP |
| Full seven-gate chain from system-flow | v1.3 establishes pipeline; gates added incrementally |
| Auth / multi-user review | Anonymous MVP |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 12 | Done (plan 12-01) |
| ARCH-02 | Phase 12 | Done (plan 12-01) |
| DATA-01 | Phase 12 | Pending |
| DATA-02 | Phase 12 | Pending |
| DATA-03 | Phase 12 | Pending |
| GEN-01 | Phase 13 | Pending |
| GEN-02 | Phase 13 | Pending |
| GEN-03 | Phase 13 | Pending |
| GEN-04 | Phase 13 | Pending |
| REV-01 | Phase 14 | Pending |
| REV-02 | Phase 14 | Pending |
| DEP-01 | Phase 15 | Pending |
| DEP-02 | Phase 15 | Pending |
