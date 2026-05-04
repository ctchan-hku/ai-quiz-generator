# Requirements — AI Quiz Generator (v1.2)

**Defined:** 2026-04-30  
**Milestone:** v1.2 — Model board & generation cost visibility  
**Core value:** Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

---

## v1.2 Requirements

Scoped work for this milestone only. **Model label / `model_used` in UI and quiz summary already exists** from prior releases; v1.2 adds **USD cost** beside that model context and improves model **selection UX** with pricing.

### MOD — Models API & catalog shape

- [x] **MOD-03**: `GET /api/models` returns each available model with **pricing fields** sufficient for comparison and client-side sort (e.g. input/output USD per million tokens or a documented comparable scalar); undocumented ids behave consistently (e.g. omit price vs explicit null — documented in README).
- [x] **MOD-04**: Config / `AVAILABLE_MODELS` (or merged catalog) remains the source of truth for **which** models are allowed; pricing aligns with deployed catalog entries where present.

### API — Generation cost

- [x] **API-COST-01**: Successful **`POST /api/generate/quiz`** response includes an **estimated USD cost** for that completion (derived from provider usage × configured or advertised rates).
- [x] **API-COST-02**: Successful **`POST /api/generate/question`** response includes the same class of **estimated USD cost** so refine flows can show spend consistently.

### FE — Model board & generation control

- [ ] **FE-MB-01**: Replace the legacy model selector with a **model board** populated from **`GET /api/models`**, showing **labels and prices** from the API.
- [ ] **FE-MB-02**: User can **sort** the board by price **ascending** or **descending**.
- [ ] **FE-MB-03**: User **selects one model** from the board for quiz and per-question generation (invalid/stale selection handled without silent wrong-model calls).
- [ ] **FE-GEN-01**: While a generation request is in flight, user can **Stop** to **abort** the request; UI returns to a safe idle state without discarding an existing quiz unrelated to the aborted call.

### FE — Cost visibility

- [ ] **FE-COST-01**: After a **successful** full-quiz generate, the UI shows **USD cost together with** the **model used** (same surface where model is already shown — add cost).
- [ ] **FE-COST-02**: **Quiz summary** includes **USD cost** alongside the **model** (extend existing summary, do not remove model).

---

## Deferred (not v1.2)

| Item | Note |
|------|------|
| Historical spend aggregation / account totals | Anonymous MVP |
| Server-enforced spend caps | Out of scope |
| Real-time streaming token ticker | Optional future |

---

## Out of scope (v1.2)

| Feature | Reason |
|---------|--------|
| Document upload track | Separate milestone |
| New question types | Unchanged |
| Changing provider billing — only **estimate** from usage + known rates | MVP transparency |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MOD-03 | Phase 10 | Done (plan **10-01** / wave 1) |
| MOD-04 | Phase 10 | Done (plan **10-01** / wave 1) |
| API-COST-01 | Phase 10 | Done (plan **10-02** / wave 2) |
| API-COST-02 | Phase 10 | Done (plan **10-02** / wave 2) |
| FE-MB-01 | Phase 11 | Pending |
| FE-MB-02 | Phase 11 | Pending |
| FE-MB-03 | Phase 11 | Pending |
| FE-GEN-01 | Phase 11 | Pending |
| FE-COST-01 | Phase 11 | Pending |
| FE-COST-02 | Phase 11 | Pending |

**Coverage:** v1.2 requirements **10** · Mapped **10** · Unmapped **0**

---

*Requirements defined: 2026-04-30*
