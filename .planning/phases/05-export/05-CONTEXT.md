# Phase 5: Export - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

<domain>
## Phase Boundary

After a quiz is generated and shown on the review screen, the user can **copy the quiz as readable plain text** (questions, options, answer key) and **download the `questions` array as a JSON file** — no server round-trip. Scoped to **EXP-01** and **EXP-02**; no new backend routes, no persistence, no export formats beyond these two.

</domain>

<decisions>
## Implementation Decisions

### UI placement and chrome

- **D-01:** Add an **export control strip** on the **review** surface: implement as a dedicated `ExportPanel` (or equivalent) rendered **inside or immediately above** the question grid, not on the idle form — users only export after `state.status === 'reviewing'`.
- **D-02:** Use existing **utility classes** already in the app (`btn-primary`, secondary outline pattern if present, `card`) — **do not add shadcn/ui** for this phase; `package.json` has no shadcn deps and Phase 3 used Tailwind + plain buttons throughout.
- **D-03:** **Success feedback:** After successful clipboard copy, show a **short inline confirmation** (e.g. “Copied!” for ~2s via local state) or `role="status"` text — **no new toast library** unless a later milestone standardizes one.

### Plain text format (EXP-01)

- **D-04:** One block of plain text suitable for email/notes: for each **multiple-choice** question, emit numbered question, options labeled **A–D** (same as `QuizDisplay`), then an **Answer:** line with the correct letter(s); include **Explanation:** on a following line when `explanation` is non-empty.
- **D-05:** For non-`multiple_choice` items in `questions[]` (forward-compatible union), emit a one-line stub: unsupported type + `question` text — do not crash export.
- **D-06:** Optionally prepend a single header line with **`model_used`** and **`source`** for context; keep the body readable (not JSON).

### JSON download (EXP-02)

- **D-07:** Download payload is **`JSON.stringify(quiz.questions, null, 2)`** — the **`questions` array only**, per requirement wording (not the full `QuizResponse` envelope unless product later expands scope).
- **D-08:** Filename pattern **`quiz-{slug}-{YYYYMMDD-HHmm}.json`** where `slug` is derived from the **current topic string** passed from `App` (slugify: lowercase, trim, spaces→hyphens, strip unsafe path chars, max ~40 chars); if topic is empty, use **`quiz`** only + timestamp.
- **D-09:** Use **`Blob` + `URL.createObjectURL` + programmatic `<a download>`** (or `showSaveFilePicker` only if we explicitly add it later — default is anchor download for broad browser support).

### State machine integration

- **D-10:** **Optional:** Dispatch `ENTER_EXPORTING` / `EXIT_EXPORTING` around clipboard/download handlers if the flow needs to block double-clicks or show a global state — **acceptable** to keep export logic **local to `ExportPanel`** with button `disabled` during in-flight copy if clipboard is async; do not leave the machine stuck in `exporting`.
- **D-11:** Clipboard failures (`NotAllowedError`, missing `navigator.clipboard`) → show **`role="alert"`** message in the panel with actionable text (user gesture required / HTTPS).

### Props / data flow

- **D-12:** **`QuizDisplay`** should receive **`topic: string`** (or `exportFilenameBase`) from **`App.tsx`** in addition to `quiz`, so exports can name files and include topic in plain-text header without lifting `QuizResponse` shape.

### Claude's Discretion

- Exact spacing/typography of the export panel; minor plain-text formatting (blank lines between questions); whether copy button uses `lucide-react` `Copy` icon matching `QuizForm` icon usage.

</decisions>

<specifics>
## Specific Ideas

- Roadmap examples (`Q1: … A) … B) … Answer: B`) are illustrative — match **A–D labels** to match live `QuizDisplay` for consistency.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` — § Phase 5: Export (success criteria, plans)
- `.planning/REQUIREMENTS.md` — EXP-01, EXP-02 (v1 Requirements)
- `.planning/STATE.md` — current phase focus

### Types and UI integration

- `frontend/src/types/quiz.ts` — `QuizResponse`, `QuizQuestion`, `MultipleChoiceQuestion`
- `frontend/src/components/QuizDisplay.tsx` — review layout, A–D labels, `correct_indices` handling
- `frontend/src/hooks/useQuizMachine.ts` — `ENTER_EXPORTING` / `EXIT_EXPORTING` if wired
- `frontend/src/App.tsx` — where `QuizDisplay` is mounted; lift `topic` for export naming

### Prior UI patterns

- `frontend/src/components/QuizForm.tsx` — button/classes patterns (`btn-primary`, `card`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`QuizDisplay`**: Renders MCQ with `LABELS = ['A','B','C','D']`; reuse the same labeling logic or share a small `formatQuizPlainText(quiz, topic?)` helper in `lib/` or next to `ExportPanel`.
- **`useQuizMachine`**: Already defines `exporting` transitions — can be used if we want global disabling during export.

### Established Patterns

- **Tailwind v4** + CSS variables (`--color-*`); no shadcn primitives in repo.
- **Lucide** icons used in `QuizForm` — optional for export buttons.

### Integration Points

- **`App.tsx`**: Pass `topic` into `QuizDisplay`; render export UI only when `state.status === 'reviewing' && state.quiz`.

</code_context>

<deferred>
## Deferred Ideas

- **PDF / Markdown export** — out of scope (see `REQUIREMENTS.md` v2 / out of scope).
- **`showSaveFilePicker` / PWA share sheet** — optional enhancement; not required for MVP checklist.
- **Full `QuizResponse` JSON download** — deferred unless product changes EXP-02; context locks to `questions[]` only.

### Reviewed Todos (not folded)

- None — `gsd-sdk` todo match not run.

</deferred>

---

*Phase: 05-export*
*Context gathered: 2026-04-24*
