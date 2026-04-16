# Issue Card Command

Help the user write a structured issue card. Ask for any missing context, then output a ready-to-paste issue using the format below.

---

## Tags

| Tag | Values | Usage |
|-----|--------|-------|
| **Type** | `bug` \| `enhancement` \| `feature` \| `chore` | Classify the work item |
| **Repo** | `backend` \| `frontend` \| `cms` | Map: gi-2.0-backend→backend, gi-2.0-frontend→frontend, gi-2.0-cms→cms |
| **Priority** | `low` \| `medium` \| `high` \| `critical` | Per incident prioritization matrix |

### Priority Matrix

- **critical** — System down, data loss, security breach; widespread impact
- **high** — Major feature broken; significant user impact; no workaround
- **medium** — Feature degraded; workaround exists; limited impact
- **low** — Minor issue; cosmetic; negligible impact

---

## Template

```
**Labels:** `type:<bug|enhancement|feature|chore>` `repo:<backend|frontend|cms>` `priority:<low|medium|high|critical>`

---

## Issue
[1–2 sentences describing the problem or request. Be specific and factual.]

## Steps to Reproduce
1. [First action]
2. [Second action]
3. [Last action]

## Results

**Expected:** [Desired outcome]

**Actual:** [What actually happens]
```

---

## Guidelines

- Be concise and professional
- Use present tense for descriptions
- Prefer bullets/lists where they improve clarity
- Do not pad with filler; only include relevant details
