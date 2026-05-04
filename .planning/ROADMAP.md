# Roadmap — AI Quiz Generator

**Version:** v1.2 — Model board & generation cost visibility  
**Last updated:** 2026-05-04  
**Prior shipped:** [v1.1 milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) (Phases 6–9)

---

## Phases

Numbering continues from v1.1 (**Phase 9** complete → **Phase 10** starts this milestone).

- [x] **Phase 10: Models API pricing + generate cost fields** — Extend **`GET /api/models`** with pricing metadata from config/catalog; add **estimated USD cost** (and underlying usage as needed) to **`POST /api/generate/quiz`** and **`POST /api/generate/question`** success bodies; tests + README / `.env.example` as needed (**MOD-03**, **MOD-04**, **API-COST-01**, **API-COST-02**) *(completed 2026-05-04)*

- [ ] **Phase 11: Model board, sort, stop, cost in UI** — Replace selector with **price-aware model board** from `/api/models`; **sort** price asc/desc; **Stop** aborts in-flight fetch; show **USD cost with model** after successful generates and in **quiz summary** (**FE-MB-01…03**, **FE-GEN-01**, **FE-COST-01**, **FE-COST-02**)

---

## Phase details

### Phase 10: Models API pricing + generate cost fields

**Goal:** Backend exposes comparable prices per model and returns a defensible **USD estimate** per successful generation call.

**Depends on:** v1.1 complete  

**Requirements:** MOD-03, MOD-04, API-COST-01, API-COST-02  

**Success criteria:**

1. `GET /api/models` documents and returns pricing fields for each listed model (or explicit absence) consistent with deployment config.
2. Quiz generate response schema includes **`cost_usd`** (or agreed field name) populated on success from completion usage.
3. Question regenerate response includes the same cost field on success.
4. Automated tests cover schema/parsing; invalid models still **422**.

---

### Phase 11: Model board, sort, stop, cost in UI

**Goal:** Users compare models by price, cancel stuck jobs, and see **cost + model** after generation and in the summary.

**Depends on:** Phase 10  

**Requirements:** FE-MB-01, FE-MB-02, FE-MB-03, FE-GEN-01, FE-COST-01, FE-COST-02  

**Success criteria:**

1. Model board loads from **`GET /api/models`** and displays prices; user picks one model for subsequent calls.
2. Toggle or control sorts by price ascending and descending.
3. **Stop** cancels the active request and leaves existing quiz data intact when aborting a redundant call.
4. Post-success UI and quiz summary show **USD cost** next to **model** text.

---

## Progress

| Phase | Status | Target |
|-------|--------|--------|
| 10. Models API + cost fields | Complete (backend); verify UAT | v1.2 |
| 11. FE board, stop, cost UX | Not started | v1.2 |

---

## Milestones index

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md)
- ✅ [v1.1 Generation quality & control](milestones/v1.1-ROADMAP.md)
- **v1.2** — this file (active)
