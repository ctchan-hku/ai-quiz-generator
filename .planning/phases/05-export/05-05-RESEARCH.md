<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-13:** A **normal web app cannot** choose a **constant folder path** (e.g. `C:\Data\quizzes.json`) or **silently append** to an existing file on disk. Downloads are **user-initiated blobs**; the browser lands them in the default Downloads folder (or a picker) per save.
- **D-14:** **Append semantics** are implemented as: a **journal object** persisted under a **stable `localStorage` key** (e.g. `mastery-exec-quiz-export-journal`). Each export **pushes** a new `QuizExportRecord` into `journal.quizzes`. **Downloading** serializes **the whole journal** (`JSON.stringify(journal, null, 2)`) so the user always gets **all appended quizzes in one JSON**. *Metaphor:* the journal is the “one growing file”; the physical file on disk is whatever the user saves/overwrites when they download.
- **D-15:** Provide **`Clear journal`** (confirm dialog) so users can reset storage without hunting devtools. Document in UI that clearing is **local to this browser** only.
- **D-16:** If journal size risks **`localStorage` ~5MB** limits, **Claude’s discretion** to switch persistence to **IndexedDB** for the same schema — only if needed after measuring typical payloads.
- **D-18:** **Submit export** (primary action): validate nothing heavy — trim comments; build **`QuizExportRecord`**; **append** to journal; trigger **download** of full journal JSON (see **D-20**).
- **D-19:** **Copy to clipboard** (EXP-01) can either **ignore comments** or append a **“Notes:”** section per question if non-empty — implementer’s choice; if included, keep plain-text readable.
- **D-20:** Top-level **journal** document schema.
- **D-21:** Each **`QuizExportRecord`** schema.
- **D-22:** **`questions[]` in the record** mirrors API/UI meaning: same fields as `MultipleChoiceQuestion` where applicable; **`comment`** is always a string (possibly `""`). For non-MC items (if ever present), still emit `comment` and best-effort fields per `QuizQuestion` union.
- **D-23:** Filename for journal download: **`quiz-export-journal.json`** or **`quiz-export-journal-{YYYYMMDD-HHmm}.json`** — **Claude’s discretion**; prefer **stable basename** so users can **overwrite** the same file in their Downloads folder manually if they want “one file on disk.”
- **D-01:** **Export / comment** flow lives on the **review** surface after `state.status === 'reviewing'`.
- **D-02:** Use existing **Tailwind** utility patterns (`btn-primary`, `card`, `input`) — **no new shadcn** dependency.
- **D-03:** Short **inline** success copy (“Download started” / “Copied!”) — no new toast library.
- **D-04:** Numbered MCQ, **A–D** labels aligned with `QuizDisplay`, **Answer:** line, **Explanation:** when present.
- **D-05:** Non-MC stub lines in plain text export.
- **D-06:** Optional header with `model_used` / `source`.
- **D-11:** Clipboard failures → `role="alert"` guidance.
- **D-12:** Pass **`topic`** from **`App.tsx`** into the export surface for `QuizExportRecord.topic` and plain-text header.
- **D-10:** **Optional** `ENTER_EXPORTING` / `EXIT_EXPORTING` while the export panel is active or during download — do not leave stuck in `exporting`.

### Claude's Discretion
- Export panel layout (collapsible per question vs all visible); lucide icons; IndexedDB vs localStorage; exact download filename; whether clipboard includes comments.

### Deferred Ideas (OUT OF SCOPE)
- **File System Access API** (`showSaveFilePicker` + writable) for true “pick once, append on disk” — power-user follow-up; not required for EXP-03.
- **Backend persistence** for shared / cross-device logs — separate phase.
- **PDF / Markdown export** — v2 / out of scope.
</user_constraints>

# Phase 5: Export - Research

**Researched:** 2026-04-24
**Domain:** React UI Layout, State Management, Local Storage
**Confidence:** HIGH

## Summary

The user requested a redesign of the UI structure to remove `ExportPanel`, attach comments directly to each question in the review view (`QuizDisplay`), and move the journal to an always-visible sidebar. This requires lifting the `comments` state up to `App.tsx` (or a dedicated layout component) so it can be passed down to both the `QuizDisplay` (for rendering textareas) and the new `JournalSidebar` (for recording the quiz with comments). The main layout in `App.tsx` will need to switch from a single-column `max-w-4xl` to a two-column layout (e.g., `flex-col md:flex-row max-w-7xl`) to accommodate the sidebar.

**Primary recommendation:** Lift comment state to `App.tsx`, modify `App.tsx` to use a two-column flex layout on desktop, add comment textareas to `QuizDisplay`, and extract the journal/export logic into a new `JournalSidebar` component.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Comment State | Browser / Client (`App.tsx`) | — | Must be shared between `QuizDisplay` (input) and `JournalSidebar` (export action). |
| Quiz Layout | Browser / Client (`App.tsx`) | — | Needs to arrange the main quiz content and the new always-visible sidebar. |
| Question Rendering | Browser / Client (`QuizDisplay`) | — | Renders the question, options, explanation, and now the comment textarea. |
| Journal & Export Actions | Browser / Client (`JournalSidebar`) | — | Handles recording the quiz, clearing the journal, and exporting the JSON file. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 19.x | UI Components & State | Project standard. |
| Tailwind CSS | 4.x | Styling & Layout | Project standard, used for responsive grid/flex layouts. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Lifting state to `App.tsx` | React Context | Context avoids prop drilling, but since the component tree is shallow (`App` -> `QuizDisplay` / `JournalSidebar`), lifting state is simpler and avoids boilerplate. |

## Architecture Patterns

### System Architecture Diagram

```
User Input (Comments) -> QuizDisplay (Textareas)
                              |
                              v
                        App.tsx (State: comments[])
                              |
                              v
User Action (Record) -> JournalSidebar (Buttons) -> LocalStorage (Journal)
```

### Recommended Project Structure
```
frontend/src/
├── components/
│   ├── QuizDisplay.tsx     # Updated to accept comments and onCommentChange
│   ├── JournalSidebar.tsx  # New component replacing ExportPanel
│   └── ...
├── lib/
│   └── quiz-export/        # Existing logic (journal.ts, clipboard.ts) remains unchanged
└── App.tsx                 # Updated layout and state management
```

### Pattern 1: Lifting State for Shared Access
**What:** Move the `comments` state from the removed `ExportPanel` up to `App.tsx`.
**When to use:** When sibling components (`QuizDisplay` and `JournalSidebar`) need access to the same state.
**Example:**
```tsx
// In App.tsx
const [comments, setComments] = useState<string[]>([]);

// Reset comments when a new quiz is generated
useEffect(() => {
  if (state.quiz) {
    setComments(state.quiz.questions.map(() => ""));
  }
}, [state.quiz]);

// Pass to QuizDisplay
<QuizDisplay quiz={state.quiz} comments={comments} onCommentChange={handleCommentChange} />

// Pass to JournalSidebar
<JournalSidebar quiz={state.quiz} topic={topic} comments={comments} />
```

### Anti-Patterns to Avoid
- **Anti-pattern:** Keeping `comments` state inside `QuizDisplay` and using an imperative handle (ref) to extract them when the user clicks "Record" in the sidebar. This breaks React's declarative data flow.
- **Anti-pattern:** Making the sidebar fixed (`position: fixed`) without adjusting the main content margin, causing overlap. Use a flex or grid layout instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Two-column layout | Custom CSS floats/positioning | Tailwind `flex` or `grid` | Tailwind provides robust, responsive utility classes (`flex-col md:flex-row`). |

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `localStorage` key `mastery-exec-quiz-export-journal` | None. The storage schema and logic remain identical. |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts | `ExportPanel.tsx` | Delete `frontend/src/components/ExportPanel.tsx` after migrating its logic to `JournalSidebar.tsx`. |

## Common Pitfalls

### Pitfall 1: Stale Comments State
**What goes wrong:** When a new quiz is generated, the comments from the previous quiz remain in the textareas.
**Why it happens:** The `comments` state in `App.tsx` is not reset when `state.quiz` changes.
**How to avoid:** Use a `useEffect` in `App.tsx` that depends on `state.quiz` (or `state.reviewGeneration`) to reset the `comments` array to empty strings matching the new question count.

### Pitfall 2: Sidebar Mobile Responsiveness
**What goes wrong:** The sidebar squishes the main content on small screens.
**Why it happens:** Using a strict row layout without wrapping.
**How to avoid:** Use `flex-col md:flex-row`. On mobile, the sidebar will stack below (or above) the main content.

## Code Examples

Verified patterns from official sources:

### Responsive Two-Column Layout
```tsx
<div className="mx-auto flex min-h-svh max-w-7xl flex-col md:flex-row gap-6 px-4 py-8">
  <main className="flex-1 flex flex-col gap-6 min-w-0">
    {/* Main content: Form, QuizDisplay */}
  </main>
  <aside className="w-full md:w-80 shrink-0">
    {/* JournalSidebar */}
  </aside>
</div>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `ExportPanel` at bottom | `JournalSidebar` on side | Phase 5 Redesign | Better visibility of journal, comments directly attached to context (questions). |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The sidebar should stack below the main content on mobile screens. | Architecture Patterns | Poor mobile UX if the sidebar is expected to be a drawer or hidden. |

## Open Questions

1. **Clipboard Copy Button Placement**
   - What we know: The "Copy to clipboard" button was previously in the `ExportPanel` alongside a preview.
   - What's unclear: Should the preview remain in the sidebar, or just a simple "Copy to clipboard" button?
   - Recommendation: Move the "Copy to clipboard" button and the preview logic into the `JournalSidebar` to keep export actions grouped.

## Environment Availability

Step 2.6: SKIPPED (no external dependencies identified)

## Sources

### Primary (HIGH confidence)
- React Documentation - Lifting State Up
- Tailwind CSS Documentation - Flexbox & Grid

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Standard React/Tailwind patterns.
- Architecture: HIGH - Simple state lifting and layout adjustment.
- Pitfalls: HIGH - Known React state lifecycle behaviors.

**Research date:** 2026-04-24
**Valid until:** 2026-05-24

## RESEARCH COMPLETE

**Phase:** 05 - Export
**Confidence:** HIGH

### Key Findings
- `comments` state must be lifted to `App.tsx` to be shared between `QuizDisplay` and the new `JournalSidebar`.
- `App.tsx` layout needs to change from `max-w-4xl flex-col` to `max-w-7xl flex-col md:flex-row` to accommodate the sidebar.
- `ExportPanel.tsx` will be deleted and its journal/export logic moved to `JournalSidebar.tsx`.
- `QuizDisplay.tsx` will be updated to accept `comments` and `onCommentChange` props, rendering a textarea for each question.

### File Created
`.planning/phases/05-export/05-05-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Standard React/Tailwind. |
| Architecture | HIGH | Clear state lifting path. |
| Pitfalls | HIGH | Known React lifecycle issues. |

### Open Questions
- Should the "Copy to clipboard" preview remain in the sidebar, or just the button? (Recommended: Keep preview in sidebar).

### Ready for Planning
Research complete. Planner can now create PLAN.md files.
