---
phase: 11
slug: model-board-sort-stop-cost-in-ui
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-05-04
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | TypeScript compile (no Vitest/Jest) |
| **Config file** | `frontend/tsconfig.json`, `frontend/eslint.config.js` |
| **Quick run command** | `cd frontend && npm run build` |
| **Full suite command** | `cd frontend && npm run build && npm run lint` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npm run build`
- **After every plan wave:** Run `cd frontend && npm run build && npm run lint`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 1 | FE-MB-01…03 | — | N/A — UI catalog only | build | `cd frontend && npm run build` | ✅ | ⬜ pending |
| TBD | 02 | 2 | FE-GEN-01, FE-COST-01…02 | — | N/A — no secrets in UI | build+lint | `cd frontend && npm run build && npm run lint` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers phase requirements — no new test framework; use `npm run build` / `npm run lint` per `11-RESEARCH.md` §9.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Sort order, board UX, Stop/cancel, cost in summary | FE-MB-02, FE-GEN-01, FE-COST-* | Browser behavior + network abort | Follow UAT matrix in `11-RESEARCH.md` §9 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
