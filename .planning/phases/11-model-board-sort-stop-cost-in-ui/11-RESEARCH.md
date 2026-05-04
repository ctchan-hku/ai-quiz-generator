# Phase 11 — Research: Model board, sort, Stop, cost in UI

Research target: answer **what to know before PLAN** for FE-MB-01…03, FE-GEN-01, FE-COST-01–02 after Phase **10** backend shipped.

---

## 1. Executive summary

The frontend already loads models via **`useQuery`** → **`listModels()`** (`frontend/src/App.tsx`, `frontend/src/lib/api.ts`) and resolves selection with **`pickedModel`** + **`resolvedModel`** (fallback to first catalog id when pick is stale or empty). **`ModelField`** remains a `<select>` with only **`id`** / **`label`**; **`ModelInfo`** in `frontend/src/types/api.ts` does **not** yet include **`price`**, unlike the Phase **10** API. **`QuizResponse.cost_usd`** exists in **`frontend/src/types/quiz.ts`** but is **never shown** in **`QuizDisplay`**, **`buildQuizClipboardText`**, **`QuizExportRecord`**, or **`JournalSidebar`**.

Implementing Phase **11** means: widening **`ModelInfo`**, replacing **`ModelField`** with a selectable board + sort UI, aligning **`axios`** calls with **`AbortController`** plus a reducer path that restores **`idle`** vs **`reviewing`** after cancellation without firing **`GENERATE_ERROR`**, and threading **`cost_usd`** into summary surfaces (possibly bumping **`EXPORT_JOURNAL_SCHEMA_VERSION`** when persisting).

---

## 2. Current codebase snapshot (paths)

| Concern | Location | Notes |
|--------|-----------|-------|
| App wiring | `frontend/src/App.tsx` | **`modelsQuery`** (`queryKey: ['models']`), **`resolvedModel`**, passes **`models`**, **`onModelChange`**, **`isGenerating`** to **`QuizForm`**, **`resolvedModel`** to **`QuizDisplay`**. |
| API client | `frontend/src/lib/api.ts` | **`listModels()`** → **`GET /api/models`**. **`generateQuiz`**, **`generateQuestion`** POST with **`api`** axios instance (**no `signal`** today). **`getRequestErrorMessage`** parses FastAPI **`detail`**. |
| Types | `frontend/src/types/api.ts` | **`ModelInfo`**: `id`, `label` only. |
| Quiz / cost types | `frontend/src/types/quiz.ts` | **`QuizResponse`**: **`model_used`, `cost_usd`, …**. **`QuestionGenerateResponse`**: includes **`cost_usd`** but see §7. |
| State machine | `frontend/src/types/quiz-machine.ts` | **`START_GENERATE`** does **not** clear **`baseQuizResponse`**; **`buildResolvedQuizResponse`** copies **`cost_usd`** from **`base`**. Good for surviving abort if status is rewound without clearing payloads. |
| Hook | `frontend/src/hooks/useQuizMachine.ts` | **`generateMutation`** (**`mutationFn`: `generateQuiz`**), **`refineMutation`** (**`generateQuestion`**). **`onMutate`** → **`START_GENERATE`**. No cancel API exposed. **`refine`** returns only **`data.question`** — **`cost_usd`** from refine response is discarded at API boundary. |
| Form | `frontend/src/components/QuizForm/QuizForm.tsx`, `ModelField.tsx`, `types.ts` | Submit guards (models loading/error empty). **`ModelField`** selects by **`models.map`** labels only. **`onModelChange`** is **`SetStateAction<string \| null>`** from App but `<select>` passes **`e.target.value`** (non-null string) — acceptable; board should preserve **`null` → first valid`** semantics via **`resolvedModel`**. |
| Review UI | `frontend/src/components/QuizDisplay.tsx` | Header shows **`quiz.model_used`** only (lines ~76–78). **`handleConfirmRefine`** passes **`resolvedModel`**. |
| Clipboard summary | `frontend/src/lib/quiz-export/clipboard.ts` | **`buildQuizClipboardText`**: **`Model: ${quiz.model_used} · Source:`** — no cost. |
| Journal | `frontend/src/types/export-journal.ts`, `frontend/src/lib/quiz-export/journal.ts`, **`JournalSidebar.tsx`** | **`QuizExportRecord`**: **`model_used`**, no **`cost_usd`**. **`buildQuizExportRecord`** omits cost. Sidebar expand shows **`Model: {q.model_used}`**. |
| Actions sidebar | `frontend/src/components/CurrentQuizActions.tsx` | Preview/copy uses **`buildQuizClipboardText`**. Record uses **`buildQuizExportRecord`**. |
| Backend route | `backend/app/routers/models.py` | Returns **`request.app.state.models_catalog`** fallback **`settings.available_models`**. Shape built in **`build_api_models_catalog`**. |

---

## 3. Backend contract — `ModelInfo` / pricing (Phase 10)

**Canonical shape** (normalized in `backend/app/helpers/model_catalog.py` via **`normalize_model_entry`**):

- **`id`**: string  
- **`label`**: string (defaults to **`id`** if missing in env JSON)  
- **`price`**: **`{ input: float | null, output: float | null }`** — USD **per 1 million tokens** for prompt vs completion respectively (explicit **`null`** when unknown / omitted; merge from **`poe_ai_models.json`** when id matches unless env row defines explicit price — see **`merge_reference_prices_into_catalog`** and Phase **10** summary **`10-01-SUMMARY.md`**).

**Frontend typing recommendation**

- Extend **`ModelInfo`** in `frontend/src/types/api.ts` to:

```ts
export interface ModelPrice {
  input: number | null
  output: number | null
}

export interface ModelInfo {
  id: string
  label: string
  price?: ModelPrice // optional for defensive parsing if older caches exist
}
```

Prefer **required `price`** with **`null` fields inside** once contract is assumed stable (`listModels()` already trusts array shape).

**Display**

- Format each side as **`$x.xx/M input`**, **`$x.xx/M output`**, hiding or showing **“Pricing unavailable”** when both **`null`** (or when entire **`price`** missing).

---

## 4. Model board UX

**Layout options**

| Pattern | Pros | Cons |
|---------|------|------|
| **Responsive grid of cards** (e.g. `grid` + **`role="radiogroup"`** with per-card **`role="radio"`** or native **`<input type="radio">`**) | Scannable comparison; suits many models | Needs min width / wrap rules |
| **Dense list/table** | Works on narrow viewports | Less “board” feel; still fine for v1.2 |

**Accessibility**

- Associate group label (**“Model”**) with **`aria-labelledby`** or **`<fieldset>` + `<legend>`**.  
- Selected state: **`aria-checked`** / checked radio + visible border/ring consistent with **`btn-*`** / **`card`** styles.  
- Keyboard: radios natively arrow-key within group; ensure focus styles match Tailwind defaults.

**Loading / errors**

- Reuse **`modelsLoading`**, **`modelsError`** contracts from **`ModelField`** (`role="alert"` on errors).

**Stale / partial data**

- If **`GET /api/models`** returns rows without **`price`**, render label + **`id`** and treat sort key as §5.

---

## 5. Sort (asc/desc price)

**Sort key**

- Use a single **scalar** comparable to Phase **10** “comparison” intent: e.g. **`sortKey = (normalizedInput ?? Number.POSITIVE_INFINITY) + (normalizedOutput ?? Number.POSITIVE_INFINITY)`**  
  — or **`max(input,output)`** if product prefers “worst-case lane”; pick one scalar in PLAN and document it.

**Tie-breaking (stable UX)**

1. **`label`** **`localeCompare`** (case-sensitive or default locale).  
2. **`id`** as final tie-breaker so order is deterministic.

**Where to sort**

- Sort a **memoized copy**: `useMemo(() => sortModels(models, direction), [models, direction])` in **`App.tsx`** or inside a renamed **`ModelField` / `ModelBoard`** wrapper so **`resolvedModel`** / **`pickedModel`** validation still runs against **unsorted or sorted** ids (ids unchanged; sorting is cosmetic).

---

## 6. Abort / Stop (`FE-GEN-01`)

**HTTP**

- Axios accepts **`signal`** on each request: `api.post(url, body, { signal })`. Extend **`generateQuiz`** / **`generateQuestion`** to accept **`signal?: AbortSignal`** (optional last arg or options object).

**TanStack Query v5**

- Prefer **`mutation.mutate(vars, { signal })`** passing an **`AbortController`** **`signal`** created per click on Generate / Confirm refinement; keep **`controller`** in **`useRef`**. **`Stop`** calls **`controller.abort()`**. Confirm against current `@tanstack/react-query` (^5.99) docs: aborted mutations should settle without treating as **`onError`** for user messaging — **`isAxiosError`** + **`error.code === 'ERR_CANCELED'`** / **`CanceledError`** (axios v1).

**Reducer / UX states**

| Flow | Desired behavior |
|------|------------------|
| **Full quiz**: user on **`reviewing`**, submits new quiz, then Stop | **`START_GENERATE`** already leaves **`baseQuizResponse`** intact; rewind **`status`** to **`reviewing`**, **`error: null`**, **`isGenerating: false`** (mutation reset). Existing quiz stays visible (**`quiz`** should match last successful resolve — unchanged until new success). |
| **Full quiz**: first load, **`idle`**, generates, then Stop | Rewind to **`idle`** (same as cancel before first completion). **`baseQuizResponse`** remains **`null`**. |
| **Refine**: Stop during **`generateQuestion`** | Do **not** **`APPEND_QUESTION_VERSION`**. **`refineMutation.reset()`** or idle refine UI; **`refiningIndex`** null. Preserve **`quiz`** unchanged. |

**Gap today**: There is **`no`** **`GENERATE_ABORTED`** action — **`onError`** always maps to **`GENERATE_ERROR`** → **`ErrorState`**, clearing the “happy path” unexpectedly on cancel. PLAN must add **`onError`** branch + **`GENERATE_ABORTED`** (`OR` **`mutation`** meta) so cancel ≠ failure.

**UI placement**

- **Stop** beside **Generating…** (replace or supplement **`LoadingState`** in **`App.tsx`**) active only while **`generateMutation.isPending`**; optional second Stop on refine (**`refineMutation.isPending`**) scoped to **`FE-GEN-01`** wording (“generation request”).  

**Idle after abort**

- **`isGenerating` false**, **`status`** **`idle`/`reviewing`**, **`error`** cleared; **`LoadingState`** unmounted.

**Distinguish full-quiz vs refine**

- Separate **`AbortController`** refs (**`quizAbortRef`**, **`refineAbortRef`**) so stopping one lane does not cancel the other.

---

## 7. Cost display (`FE-COST-01`, `FE-COST-02`)

**Formatting**

- Use **`Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 4 })`** — or clamp fraction digits based on magnitude of **`cost_usd`** (Planner choice).

**`FE-COST-01`** (after successful full-quiz generate)

- **`QuizDisplay`** header (**same card**, ~lines 76–78): add **`Estimated cost`** (or **`~$`** if estimate) next to **`model_used`**, sourced from **`quiz.cost_usd`**.

**`FE-COST-02`** (quiz summary)

- **`buildQuizClipboardText`**: extend the **`Model:`** line — e.g. **`Model: ${quiz.model_used} · Cost (est.): … · Source:`**  
- **`JournalSidebar`** expanded **`Model:`** row: append cost when **`QuizExportRecord`** carries it.

**Journal / JSON export**

- Today **`QuizExportRecord`** (**`frontend/src/types/export-journal.ts`**) has no **`cost_usd`**. Options: **`(a)`** add optional **`cost_usd?: number`** without bumping **`EXPORT_JOURNAL_SCHEMA_VERSION`** (loader tolerates extras), **`(b)`** bump **`EXPORT_JOURNAL_SCHEMA_VERSION`** to **2** and adjust **`loadJournal`** drop/migrate policy — PLAN should pick **`(b)`** if strict schema hygiene is preferred.

**Refine caveat**

- **`generateQuestion`** in **`api.ts`** returns only **`question`**; **`cost_usd`** for each refinement is dropped. Resolved **`quiz`** keeps **`cost_usd`** from **first full generate** (**`buildResolvedQuizResponse`**). If product wants cumulative spend UI, PLAN needs API return change + reducer merge — **not** required by **`FE-COST-01`** as written (**full-quiz** only).

---

## 8. Risks / edge cases

- **Stale **`pickedModel`** after catalog refresh**: already mitigated by **`resolvedModel`** in **`App.tsx`**; board must **`not`** show a phantom selection — sync selection state when **`pickedModel`** not in list (reset to **`null`** or mirror **`resolvedModel`**). **`FE-MB-03`** “no silent wrong-model calls”: always submit **`resolvedModel`** (or **`formConfig.model`** derived from resolver), never unvalidated **`pickedModel`** alone.  
- **`POST` while models list stale**: **`QuizForm`** already blocks **`modelsLoading`**.  
- **Double submit**: **`submitDisabled`** when **`isLoading`**. PLAN: **`Stop`** disables submit only while redundant; **`reset`** mutation **`isPending`**.  
- **Abort vs timeout**: Axios **`timeout`** (**`HTTP_CLIENT_TIMEOUT_MS`**) fires error, not cancel — UX copy should differ from **Stop**.  
- **Rounding / zero cost**: backends may return **`0`** when rates missing — display honestly (“$0.00 est.” vs “rates missing”).  
- **Accessibility**: noisy price strings in screen readers — use **`aria-label`** concise version on cards.

---

## 9. Validation Architecture (GSD Nyquist)

**Automated**

- **`npm run build`** in `frontend` — **`tsc -b && vite build`** (catches **`ModelInfo`** / JSX prop drift).  
- **`npm run lint`** — ESLint (**no test script** in **`frontend/package.json`**; **no Vitest/Jest/React Testing Library** in dependencies).

**Manual UAT mapped to requirements**

| ID | Check |
|----|--------|
| **FE-MB-01** | Load app: board shows **`label`** + price text from live **`GET /api/models`**; loading/error paths match legacy behavior. |
| **FE-MB-02** | Toggle sort asc/desc: order reverses deterministically; unknown-price models behave per PLAN (e.g. grouped at end). |
| **FE-MB-03** | Remove selected model server-side OR swap **`AVAILABLE_MODELS`**: UI falls back without sending invalid **`model`** (`422` regression spot-check). Select model → **`network`** **`POST`** body **`model`** matches selection. |
| **FE-GEN-01** | Start generate → **Stop** before completion: **`LoadingState`** gone, no **`ErrorState`**, existing reviewed quiz unchanged if redo aborted; refinement abort does not mutate version stack. |
| **FE-COST-01** | After generate 200: header shows **`model_used`** **and** USD estimate. |
| **FE-COST-02** | Preview summary + clipboard + journal record / sidebar show cost **with** model (per PLAN schema). |

**Optional regression**

- **`pytest`** backend unaffected if frontend-only phase; rerun if touching shared env docs later.

---

## 10. Suggested plan split

**Wave 1 — Board + typing + sort + stale selection**

- **`ModelInfo`** + **`listModels`** typing; **`ModelBoard`** (replace **`ModelField`**) props: **`models`, `model` (controlled id string), `onModelChange`, sort direction + toggle, loading/error/disabled**.
- Memoized sort helpers; **`App`** passes sorted list vs raw per PLAN preference.
- Visual + a11y pass.

**Wave 2 — Stop + cost surfaces + journal**

- **`api.ts`**: **`signal`** on **`generateQuiz`**, **`generateQuestion`**.
- **`useQuizMachine`**: **`AbortController`**, **`GENERATE_ABORTED`**, **`onError`** cancel detection; expose **`cancelGenerate`**, **`cancelRefine`** (**or** unified **`abortActiveGeneration`** keyed by lane).
- **`App`**: **`Stop`** button UX; **`LoadingState`** integration.
- **`QuizDisplay`**, **`clipboard.ts`**, **`buildQuizExportRecord`**, **`export-journal.ts`**, **`JournalSidebar.tsx`**: **`cost_usd`**; schema bump decision.

---

## RESEARCH COMPLETE
