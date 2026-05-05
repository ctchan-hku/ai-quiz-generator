# Retrospective — AI Quiz Generator (living)

## Milestone: v1.2 — Model board & generation cost visibility

**Shipped:** 2026-05-05  
**Phases:** 2 | **Plans:** 4  

### What was built

- Priced **`GET /api/models`** and **`cost_usd`** on both generate endpoints.
- Model **board** + **sort**, **Stop**/abort UX, cost in **review / clipboard / journal**.
- **Backend** cancellation when the **client disconnects** (complements frontend abort).

### What worked

- Clear split **Phase 10 API** then **Phase 11 UI**; requirements traceability stayed 1:1.
- Reuse of **`model_catalog`** for both API list and cost estimation.

### What was inefficient

- _(Optional: fill after team debrief.)_

### Patterns established

- Wrapper response for single-question generate **`{ question, cost_usd }`** with FE unwrap.
- Export journal **schema_version** bump with explicit migration (clear old localStorage shape).

### Key lessons

- Starlette does not auto-cancel handlers on disconnect — explicit **race + task cancel** needed.
- **UAT** (`10-UAT.md`, `11-UAT.md`) caught cross-layer expectations early.

---

## Cross-milestone trends

| Milestone | Phases | Theme |
|-----------|--------|--------|
| v1.0 | 1–5 | Topic MCQ MVP |
| v1.1 | 6–9 | Quality & per-question refine |
| v1.2 | 10–11 | Price transparency & generation control |
