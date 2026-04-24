# Phase 5: Export - Context

**Gathered:** 2026-04-24 (updated: commented JSON + appendable journal)
**Status:** Ready for planning

<domain>
## Phase Boundary

After a quiz is generated and shown on the review screen, the user can:

1. **Copy** the quiz as readable plain text (**EXP-01**).
2. **Export JSON** that includes **full question data** (statement, options, correct answers, explanations, types) **plus optional per-question comments** (**EXP-02** / **EXP-03**).
3. **Append** multiple quiz exports into **one logical JSON document** over time via **browser storage** (fixed storage key) — each export adds a **quiz record**; downloading writes the **entire journal** to a file. **No backend**, **no fixed path on the user’s disk** (browser security).

Out of scope for this phase: PDF/Markdown export, server-side persistence, true silent append to an OS file path.

</domain>

<decisions>
## Implementation Decisions

### Where the “file” lives (append vs constant disk path)

- **D-13:** A **normal web app cannot** choose a **constant folder path** (e.g. `C:\Data\quizzes.json`) or **silently append** to an existing file on disk. Downloads are **user-initiated blobs**; the browser lands them in the default Downloads folder (or a picker) per save.
- **D-14:** **Append semantics** are implemented as: a **journal object** persisted under a **stable `localStorage` key** (e.g. `mastery-exec-quiz-export-journal`). Each export **pushes** a new `QuizExportRecord` into `journal.quizzes`. **Downloading** serializes **the whole journal** (`JSON.stringify(journal, null, 2)`) so the user always gets **all appended quizzes in one JSON**. *Metaphor:* the journal is the “one growing file”; the physical file on disk is whatever the user saves/overwrites when they download.
- **D-15:** Provide **`Clear journal`** (confirm dialog) so users can reset storage without hunting devtools. Document in UI that clearing is **local to this browser** only.
- **D-16:** If journal size risks **`localStorage` ~5MB** limits, **Claude’s discretion** to switch persistence to **IndexedDB** for the same schema — only if needed after measuring typical payloads.

### Per-question comments UI

- **D-17:** Enter **export mode** from the review screen: e.g. **“Export / add notes”** opens an **`ExportPanel`** (or inline expansion) with **one comment field per question** (`<textarea>` or single-line `input`), bound by question index; empty comment is allowed.
- **D-18:** **Submit export** (primary action): validate nothing heavy — trim comments; build **`QuizExportRecord`**; **append** to journal; trigger **download** of full journal JSON (see **D-20**).
- **D-19:** **Copy to clipboard** (EXP-01) can either **ignore comments** or append a **“Notes:”** section per question if non-empty — implementer’s choice; if included, keep plain-text readable.

### JSON schema (consistent, machine-readable)

- **D-20:** Top-level **journal** document:

```json
{
  "schema_version": 1,
  "updated_at": "<ISO-8601>",
  "quizzes": [ /* QuizExportRecord[] */ ]
}
```

- **D-21:** Each **`QuizExportRecord`**:

```json
{
  "exported_at": "<ISO-8601>",
  "topic": "<string from form>",
  "model_used": "<string>",
  "source": "topic",
  "truncated": false,
  "questions": [
    {
      "index": 0,
      "question_type": "multiple_choice",
      "question": "...",
      "options": ["A text", "B text", "C text", "D text"],
      "correct_indices": [0],
      "explanation": "...",
      "comment": ""
    }
  ]
}
```

- **D-22:** **`questions[]` in the record** mirrors API/UI meaning: same fields as `MultipleChoiceQuestion` where applicable; **`comment`** is always a string (possibly `""`). For non-MC items (if ever present), still emit `comment` and best-effort fields per `QuizQuestion` union.
- **D-23:** Filename for journal download: **`quiz-export-journal.json`** or **`quiz-export-journal-{YYYYMMDD-HHmm}.json`** — **Claude’s discretion**; prefer **stable basename** so users can **overwrite** the same file in their Downloads folder manually if they want “one file on disk.”

### UI placement and chrome

- **D-01:** **Export / comment** flow lives on the **review** surface after `state.status === 'reviewing'`.
- **D-02:** Use existing **Tailwind** utility patterns (`btn-primary`, `card`, `input`) — **no new shadcn** dependency.
- **D-03:** Short **inline** success copy (“Download started” / “Copied!”) — no new toast library.

### Plain text format (EXP-01)

- **D-04:** Numbered MCQ, **A–D** labels aligned with `QuizDisplay`, **Answer:** line, **Explanation:** when present.
- **D-05:** Non-MC stub lines in plain text export.
- **D-06:** Optional header with `model_used` / `source`.

### Clipboard and errors

- **D-11:** Clipboard failures → `role="alert"` guidance.

### Props / data flow

- **D-12:** Pass **`topic`** from **`App.tsx`** into the export surface for `QuizExportRecord.topic` and plain-text header.

### State machine integration

- **D-10:** **Optional** `ENTER_EXPORTING` / `EXIT_EXPORTING` while the export panel is active or during download — do not leave stuck in `exporting`.

### Claude's Discretion

- Export panel layout (collapsible per question vs all visible); lucide icons; IndexedDB vs localStorage; exact download filename; whether clipboard includes comments.

</decisions>

<specifics>
## Specific Ideas

- Plain-text and JSON should use the **same A–D ordering** as `QuizDisplay` (`LABELS = ['A','B','C','D']`).

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` — § Phase 5: Export
- `.planning/REQUIREMENTS.md` — EXP-01, EXP-02, EXP-03
- `.planning/STATE.md` — current phase focus

### Types and UI integration

- `frontend/src/types/quiz.ts` — `QuizResponse`, `QuizQuestion`, `MultipleChoiceQuestion`
- `frontend/src/components/QuizDisplay.tsx` — review layout, labels
- `frontend/src/hooks/useQuizMachine.ts` — optional exporting transitions
- `frontend/src/App.tsx` — pass `topic`, mount export UI when reviewing

### Prior UI patterns

- `frontend/src/components/QuizForm.tsx` — buttons / form styling

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`QuizDisplay`**: Labeling and MCQ structure — align export formatters with the same rules.
- **`useQuizMachine`**: Optional global state during export.

### Established Patterns

- **Tailwind v4**, CSS variables; **no** shadcn in `package.json`.

### Integration Points

- **`App.tsx`**: Review branch; pass `quiz` + `topic` into export/comments UI.

### New modules (suggested)

- `frontend/src/lib/exportJournal.ts` — `loadJournal`, `appendRecord`, `clearJournal`, types for `ExportJournal` / `QuizExportRecord`.
- `frontend/src/components/ExportPanel.tsx` — comments + actions.

</code_context>

<deferred>
## Deferred Ideas

- **File System Access API** (`showSaveFilePicker` + writable) for true “pick once, append on disk” — power-user follow-up; not required for EXP-03.
- **Backend persistence** for shared / cross-device logs — separate phase.
- **PDF / Markdown export** — v2 / out of scope.

### Reviewed Todos (not folded)

- None.

</deferred>

---

*Phase: 05-export*
*Context gathered: 2026-04-24*
