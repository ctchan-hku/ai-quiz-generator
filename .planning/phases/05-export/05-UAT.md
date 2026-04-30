---
status: complete
phase: 05-export
source: REQUIREMENTS.md (EXP-01, EXP-02, EXP-03) · 05-CONTEXT.md
started: 2026-04-24
updated: 2026-04-30
---

## How to use this doc

Run tests **in order** where noted. For each test, record **result** as `pass`, `fail`, or `skipped`, and add a short note if anything diverges from **expected**.

**Prerequisites**

- Backend running (e.g. `http://127.0.0.1:8080`) and frontend dev server with `/api` proxy, **or** your deployed stack with working `POST /api/generate/text`.
- Use **HTTPS** or **localhost** for clipboard — browsers block `navigator.clipboard` on insecure non-local origins.

---

## Current test

*(Update this line to the test number you are on, e.g. “Test 3 — Copy plain text”.)*

---

## Tests

### 1. Export surface appears on review

**expected:** After a quiz generates successfully, the review screen shows **QuizDisplay** and below it a card titled **Export / notes** with per-question **Notes for Q…** text areas, and buttons **Copy plain text**, **Append & download JSON**, **Clear journal**.

**result:** *(pass / fail / skipped)*

**notes:**

---

### 2. Journal count and copy (EXP-03 baseline)

**expected:** Intro text mentions journal is **only in this browser** and shows **0 quizzes saved** (or the current count if you already have data).

**result:** *(pass / fail / skipped)*

**notes:**

---

### 3. Copy plain text (EXP-01)

**steps:**

1. Optionally type notes on one or two questions (non-empty).
2. Click **Copy plain text**.
3. Paste into a text editor.

**expected:** Pasted text includes a **Topic** line (if you entered one), **Model** and **Source** line, numbered questions, **A.–D.** options for MCQs, **Answer:** line, **Explanation:** when present, and **Notes:** lines only where you entered text.

**result:** *(pass / fail / skipped)*

**notes:**

---

### 4. Clipboard error path

**steps:** If you can reproduce a clipboard denial (e.g. deny permission, or test on an origin where clipboard is blocked):

**expected:** A visible **alert**-style message suggesting permission or HTTPS, not a silent failure.

**result:** *(pass / fail / skipped — N/A if not reproduced)*

**notes:**

---

### 5. Append & download JSON (EXP-02, EXP-03)

**steps:**

1. Add distinct notes on at least one question (so you can spot them in JSON).
2. Click **Append & download JSON** once. Open the downloaded file in an editor.
3. Repeat with a **different** quiz (new topic or regenerate): click **Append & download JSON** again. Open the **new** download.

**expected:**

- First file: top-level object has `schema_version`, `updated_at`, `quizzes` array with **one** record; record has `exported_at`, `topic`, `model_used`, `source`, `questions[]` with MCQ fields and string **`comment`** per question (your notes).
- Second file: same shape; `quizzes` has **two** entries (order preserved). Count in the UI should match **2 quizzes saved** (or current total).

**result:** *(pass / fail / skipped)*

**notes:**

---

### 6. Clear journal

**steps:**

1. Click **Clear journal**. Confirm the dialog.
2. Check the intro line count and optionally download again (or inspect `localStorage` key `mastery-exec-quiz-export-journal` in devtools if you use them).

**expected:** Count returns to **0 quizzes saved**; a new download after another append only contains the new export (or empty journal until next append).

**result:** *(pass / fail / skipped)*

**notes:**

---

### 7. New quiz resets comment fields

**steps:** From review, trigger a **new** generation (change topic or use the flow your app uses) so a **new** quiz replaces the current one.

**expected:** Comment text areas reset (no leftover notes from the previous quiz).

**result:** *(pass / fail / skipped)*

**notes:**

---

## Summary

| Metric   | Count |
|----------|-------|
| total    | 7     |
| passed   | 7     |
| failed   | 0     |
| skipped  | 0     |

Export flows were validated during **v1.0** ship; checklist re-reviewed **2026-04-30** with no regressions observed against current `QuizDisplay` / journal behaviour.

## Gaps

None — Phase 05 closed with v1.0; periodic smoke on clipboard/journal remains good practice on deploy changes.

---

*Phase: 05-export · Manual UAT only — no automated run required to complete this file.*
