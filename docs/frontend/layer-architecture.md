---
title: Frontend Layer Architecture
slug: frontend-layer-architecture
summary: Four-layer model from UI to API with clear command vs domain split in lib/.
description: Defines how the ai-test-generator frontend organizes components, hooks, domain logic, and API calls. Covers dependency rules, file placement in lib/test-machine/, and anti-patterns to avoid when adding features.
---

## Overview

The frontend uses a **small, explicit layer stack**. Each layer has one job. Imports flow **downward only** — from UI toward HTTP.

```
┌─────────────────────────────────────────────────────────┐
│  UI          components/          JSX, events, layout │
├─────────────────────────────────────────────────────────┤
│  Hooks       hooks/               React wiring only     │
├─────────────────────────────────────────────────────────┤
│  Domain      lib/<feature>/       pure logic + commands │
├─────────────────────────────────────────────────────────┤
│  API         api/                 HTTP + DTO contracts  │
└─────────────────────────────────────────────────────────┘
```

Supporting folders sit beside this stack (not inside it):

| Folder | Role |
|--------|------|
| `config/` | Defaults and constants (`test-form.ts`) |
| `data/` | Static lookup tables (`model-generation-cost.ts`) |
| `components/ui/` | Design-system primitives (shadcn) — no business logic |

---

## Layer 1 — UI (`components/`)

**Job:** Render markup, capture input, invoke callbacks passed as props.

**May import:**

- `@/components/ui/*`
- `@/config/*` for display labels and captions
- `@/api/contracts` for **types only**
- `@/lib/*` for display-only helpers (`format-usd`, `mc-option-label`)

**Must not import:**

- `@/api/methods` or the `@/api` barrel when it pulls in methods
- `useMutation`, `useQuery`, `useReducer`, `dispatch`
- `localStorage` / `sessionStorage`
- `navigator.clipboard` in growing action panels (extract to a hook)

### Container vs presentational

| Kind | Signals | Example |
|------|---------|---------|
| **Container** | Uses hooks, dispatch, or queries | `App.tsx` |
| **Presentational** | Props in, JSX out | `TestQuestionCard.tsx`, `TopicField.tsx` |

> **Rule:** If a component needs `useMutation`, `useQuery`, or `dispatch`, it is a container — or it should receive behavior via props from a hook used by its parent.

### Current violations to fix (refactor plan)

- `LoginForm.tsx` owns `useMutation` → extract `hooks/useLogin.ts`
- `CurrentTestActions.tsx` owns journal + clipboard I/O → extract `hooks/useTestExportActions.ts`

---

## Layer 2 — Hooks (`hooks/`)

**Job:** Connect React lifecycle to domain commands and API. Own refs, abort controllers, mutations, queries, and effects.

**May import:** `@/lib/*`, `@/api/methods`, `@/api/contracts`, `@/api` error helpers.

**Must not contain:** Large JSX trees or pure domain transforms (those belong in `lib/`).

| Hook | Owns |
|------|------|
| `useTestMachine` | Machine reducer, generate/edit mutations, abort |
| `useAppSession` | Comments, last-review snapshot, session persist effect |
| `useModels` | `listModels` query (extract from `App.tsx`) |
| `useLogin` | Login mutation (extract from `LoginForm.tsx`) |
| `useTestExportActions` | Clipboard + journal record actions |
| `usePagination` | Generic list paging — no domain |

**Error handling:** Hooks call `getRequestErrorMessage` and pass `string | null` to UI. Components display strings; they do not interpret `unknown` errors.

---

## Layer 3 — Domain (`lib/<feature>/`)

Split by **kind of logic**, not by UI screen or machine status.

### Command vs domain vs persistence

| Kind | Naming | Pure? | Calls API? | Example file |
|------|--------|-------|------------|--------------|
| **Command** | verb or task name | No (async) | Yes | `commands.ts` → `runGenerateTest()` |
| **Domain** | noun or concept | Yes | No | `versioned-review.ts` → `appendQuestionVersion()` |
| **State** | `reducer.ts`, `types.ts` | Yes | No | `testMachineReducer()` |
| **Persistence** | `persistence.ts` | Mixed | No HTTP | `loadPersistedSession()` |

- **Commands** orchestrate external work and return a typed result.
- **Domain** functions are deterministic: same input → same output, no I/O.
- **Persistence** is the only place that touches `localStorage` for that feature.

Do **not** label pure transforms as "services." Do **not** group files by machine status (`generating/`, `reviewing/`) — status lives in the reducer.

### `lib/test-machine/` layout (canonical)

```
lib/test-machine/
├── types.ts              # state, actions, battle types
├── reducer.ts            # pure transitions + initialState
├── commands.ts           # async commands — POST /api/generate/test, …
├── versioned-review.ts   # domain — question version history
└── persistence.ts        # session localStorage
```

Other domain modules follow the same idea:

| Module | Role |
|--------|------|
| `lib/export-test/journal.ts` | Journal persistence |
| `lib/export-test/clipboard.ts` | Export text formatting |
| `lib/export-test/record-test.ts` | Command — build + append record (planned) |
| `lib/course-test-selection.ts` | Course test selection logic |
| `lib/model-board.ts` | Model cost sort helpers |

### Subfolder rule

Keep files as **siblings** inside the feature folder until a concern grows to **2+ related files**. Then add a subfolder (e.g. `lib/export-test/` already justified).

Do **not** add `lib/test-machine/index.ts` barrel re-exports (project rule PROH-03).

---

## Layer 4 — API (`api/`)

**Job:** Transport only — axios instance, serialization, typed HTTP methods.

```
api/
├── contracts.ts    # request/response types (DTOs)
├── client.ts       # axios instance
├── methods.ts      # generateTest(), login(), listModels(), …
├── case-keys.ts    # snake/camel conversion
└── config.ts       # timeouts, retry defaults
```

**Import convention:**

| Need | Import from |
|------|-------------|
| Types only | `@/api/contracts` |
| HTTP calls | `@/api/methods` (hooks and commands only) |
| Error helper | `getRequestErrorMessage` from `@/api` |

**Must not import:** `components/`, `hooks/`, `lib/`.

---

## Dependency rules

```
components  →  hooks  →  lib  →  api
                ↓
         lib (types / display helpers only from components)
```

| From → To | Allowed? |
|-----------|----------|
| UI → hooks | Yes (via parent container) |
| UI → `api/contracts` (types) | Yes |
| UI → `api/methods` | **No** |
| UI → lib display helpers | Yes |
| hooks → lib | Yes |
| hooks → api | Yes |
| lib domain → api | **No** |
| lib command → api | Yes |
| api → lib / components | **No** |

**Sanity check:** If you delete `api/`, hooks and commands fail to compile; pure domain and UI types should still typecheck with mocked data.

---

## End-to-end trace — Generate test

```
TestForm (UI)
  onSubmit(config)
    ↓
App → useTestMachine.submitGenerate(config)       [Hook]
    ↓
runGenerateTest(config, signal)                     [Command — lib/test-machine/commands.ts]
    ↓
generateTest(body, signal)                          [API — api/methods.ts]
    ↓
POST /api/generate/test
    ↓
onSuccess → dispatch(GENERATE_SUCCESS)              [Hook]
    ↓
testMachineReducer(state, action)                   [Domain — reducer.ts]
    ↓
toTestVersionedReview(response)                     [Domain — versioned-review.ts]
    ↓
TestDisplay re-renders from state                   [UI]
```

---

## One hook per external system

| External system | Owner | UI must not… |
|-----------------|-------|--------------|
| Backend HTTP | `useTestMachine`, `useLogin`, `useModels` | call `api/methods` directly |
| Session storage | `useAppSession` + `persistence.ts` | read/write `localStorage` |
| Export journal | `useTestExportActions` + `journal.ts` | call `appendTestRecord` inline |
| Clipboard | `useTestExportActions` | scatter `navigator.clipboard` calls |

---

## Anti-patterns

| Avoid | Why |
|-------|-----|
| One exported function per file | Navigation overhead without a real boundary |
| `lib/**/index.ts` barrel shims | Hides dependencies (PROH-03) |
| `features/` top-level rewrite | Unnecessary for current codebase size |
| Duplicating `contracts` as view-models | Wait until API shapes diverge from UI needs |
| Folders named by machine status | Status belongs in reducer + types |
| `services/` folder for pure functions | Mislabels domain transforms |

---

## Checklist for new code

1. **Does it change with an existing module?** → Add it there.
2. **Is it a generic React primitive?** → `hooks/` or `components/ui/`.
3. **Is the file still under ~150 lines after adding?** → Keep in the same file.
4. **Does it exceed ~200 lines or mix pure logic with React?** → Split by concern (state / command / UI), not by export count.
5. **Does it call the network?** → Command in `lib/` + wire in a hook — never in UI.
6. **Is it pure data logic?** → Domain file in `lib/<feature>/`.

---

## Related documents

- Implementation plan: [`docs/superpowers/plans/2026-06-01-frontend-refactor.md`](../superpowers/plans/2026-06-01-frontend-refactor.md)
