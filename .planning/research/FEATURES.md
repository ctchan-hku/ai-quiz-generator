# Feature Landscape — AI Quiz Generator

**Domain:** AI-powered quiz generation web app
**Researched:** 2026-04-22
**Sources:** Quizgecko, QuizWhiz, Jotform AI Quiz Generator, involve.me, comparative reviews (involve.me/blog, remnote.com, edubrain.ai)

---

## Table Stakes

Features users expect from any AI quiz generator. Missing = users leave or distrust the product.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Topic prompt → quiz** | Core use case; every competitor has it; zero friction entry point | Low | Just a text input and a Generate button |
| **Document upload → quiz** | Expected for educators/trainers; Jotform, Quizgecko, QuizWhiz all lead with it | Medium | PDF is the primary format; plain text a close second |
| **Configurable question count** | Every tool lets users pick 5/10/15/20; hardcoded count feels broken | Low | Dropdown or number input; Jotform does this in Step 2 |
| **Multiple-choice output (4 options, 1 correct)** | The dominant format; synonymous with "quiz" for most users | Low | Users expect labeled options (A/B/C/D) with a clear correct answer |
| **Visible correct answers** | Without this, the quiz is useless for self-study or review | Low | Show correct answer on the review screen, not just during quiz-taking |
| **Review screen before export** | Users must see the generated questions before committing; Jotform Step 3 | Low | List of questions + answers, scrollable |
| **Loading/generation feedback** | AI calls take 5-20s; a blank screen feels broken; need progress indication | Low | Spinner or animated "generating…" state |
| **Error handling on generation** | API failures, empty uploads, too-short prompts must surface gracefully | Low | Friendly error message, not a crashed page |
| **Clipboard copy** | Fast sharing without download friction; widely expected | Low | Copy all questions + answers as formatted text |
| **JSON export** | Developer-friendly; enables downstream use (LMS import, apps); specified in scope | Low | Structured `{question, options, correct_answer}` array |
| **Shareable public URL** | No-auth apps need a way to link someone directly to the tool | Low | Base URL of the deployed app — the whole tool is the shareable artifact |

---

## The Jotform 3-Step UX Pattern (Reference Implementation)

Jotform's flow is the UX pattern to replicate. It sets user expectation anchors.

```
Step 1 — Input
  ├── Text prompt: "Generate a quiz about [topic]"
  └── File upload: drag-and-drop or file picker (PDF, PPT, Word, text)

Step 2 — Configure
  ├── Question count (slider or dropdown: 5 / 10 / 15 / 20)
  ├── Question type selection (Jotform: MCQ, True/False, mixed)
  └── [Optional] Language, difficulty

Step 3 — Review & Share
  ├── Rendered question list with correct answers visible
  ├── Individual question editing / regeneration
  └── Export / share / embed options
```

**MVP maps directly to this flow:**
- Step 1: Topic prompt textarea + PDF/text file upload tab
- Step 2: Question count picker + model selector (our differentiator)
- Step 3: Review list + Copy to clipboard + Download JSON

The model selector fits naturally in Step 2 alongside other generation parameters. Users perceive it as a "quality knob."

---

## UX Micro-Patterns That Matter

These are implementation details that elevate feel from "prototype" to "product."

| Pattern | What It Is | Why It Matters | Effort |
|---------|-----------|----------------|--------|
| **Tabbed input** | Two tabs: "Topic" and "Upload" | Prevents a cluttered single input area | Very Low |
| **Character/file feedback** | "Prompt looks good" / "File uploaded: lecture.pdf (42KB)" | Trust signal before generation | Low |
| **Streaming or progressive reveal** | Questions appear one-by-one as they generate (streaming) | Dramatically reduces perceived wait time | Medium |
| **Question numbering** | Q1, Q2 ... with A/B/C/D labels | Standard expected structure; feels official | Very Low |
| **Correct answer highlight** | Green checkmark or bold on correct option | Visual scan speed; removes ambiguity | Very Low |
| **Regenerate all** | One-click to start over with same config | Escape hatch; reduces frustration on bad runs | Low |
| **Empty state guidance** | "Try: '10 questions about World War II' or upload a PDF" | Reduces blank-page paralysis; onboarding | Very Low |

---

## Differentiators

Features that set a product apart. Not expected at MVP, but valued. Defer unless trivially cheap.

| Feature | Value Proposition | Complexity | Defer Reason |
|---------|------------------|------------|--------------|
| **Model selection** | Power users pick GPT-4o vs cheaper models; unique to our app | Low | **Include in MVP** — already in scope, trivially a dropdown |
| **Difficulty control** | "Easy / Medium / Hard" — affects distractor quality and question depth | Low | Doable via prompt engineering; good v1.1 add if prompts allow |
| **Answer explanations** | "Why is B correct?" — huge for learning; Quizgecko does this well | Medium | Adds tokens + UI complexity; clear v2 feature |
| **True/False question type** | Second-most-common type; educators expect it | Low | Out of scope for MVP by decision; add in v1.1 |
| **Individual question regeneration** | "Re-roll this question" without regenerating everything | Medium | UI state management complexity; worth adding post-MVP |
| **Question editing** | Manually edit any question text or answer choices | Medium | Out of scope per PROJECT.md; v1.1 once core loop is stable |
| **Multiple input files** | Upload 3 lecture slides and combine | Medium | Complicates upload UX and token budgeting |
| **URL / YouTube as input** | Paste a link, AI fetches and quizzes it | High | Requires web scraping / transcript pipeline; v2 |
| **Language selection** | Generate quizzes in Spanish, French, etc. | Low | Prompt engineering change; trivially addable but not MVP |
| **PDF export** | Print-ready formatted PDF | Medium | Requires server-side rendering or jsPDF; v1.1 |
| **Progress streaming (SSE)** | Questions appear word-by-word as LLM generates | Medium | Improves perceived performance significantly; v1.1 target |
| **Quiz scoring / test mode** | Interactive quiz where user picks answers and gets scored | High | Response collection = auth = out of scope for no-persistence MVP |
| **Plausible distractor quality indicator** | "These distractors are strong / weak" | High | Requires second LLM pass for evaluation |
| **Bloom's Taxonomy alignment** | "Apply-level" vs "Remember-level" questions | Medium | Prompt engineering possible but output quality validation is hard |

---

## Anti-Features

Things to deliberately NOT build for MVP. Each one has a cost beyond its complexity.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **User accounts / auth** | Adds weeks of scope, introduces session management, kills the "frictionless" core value | Anonymous forever for MVP; if persistence is needed, add local storage first |
| **Quiz persistence / history** | Without auth, history is meaningless; with auth, see above | Users export JSON if they want to save |
| **Quiz scoring / response collection** | Turns the product from a generator into a proctoring platform (different product entirely) | Generation only; users take the quiz in their own LMS |
| **Custom branding / themes** | Significant UI configuration complexity; marginal value at MVP stage | Single clean design; good aesthetics is not the same as theming |
| **Short-answer / essay questions** | Auto-grading is AI research problem; without auto-grading, they're useless at scale | Multiple choice only for MVP |
| **LMS integrations (Canvas, Moodle)** | OAuth, API keys, institution IT approval — months of work | JSON export is the integration surface; users import manually |
| **Embedding / iFrame share** | Security, CORS, responsive sizing complexity | Shareable URL to the tool itself is sufficient |
| **Collaborative editing** | Real-time sync, conflict resolution — OT/CRDT complexity | Single-user session; no collaboration |
| **Duplicate detection** | Detecting semantically similar questions across quiz runs | Not a user complaint at MVP stage |
| **Quiz templates / categories** | Pre-built "History Quiz", "Science Quiz" starters | The prompt IS the template; keep it open-ended |

---

## Feature Dependencies

```
Topic prompt input ──────────────────────────────┐
                                                  ├── Generation API call ──┐
Document upload → text extraction (PDF parse) ───┘                         │
                                                                            │
Model selector ────────────────────────────────────────────────────────────┤
Question count picker ─────────────────────────────────────────────────────┤
                                                                            │
                                                          Quiz output ──────┤
                                                                            ├── Review screen
                                                                            ├── Clipboard copy
                                                                            └── JSON download
```

**Hard dependencies:**
- Review screen requires generation to succeed
- Clipboard copy and JSON export require review screen data
- PDF upload requires server-side PDF text extraction (before API call)
- Model selector requires knowing available models at load time (fetch from backend or hardcode)

---

## MVP Recommendation

### Include (Phase 1 + 2)

1. **Topic prompt textarea** — primary input, lowest friction
2. **PDF / text file upload** — differentiates from "just another ChatGPT wrapper"
3. **Question count picker** — 5 / 10 / 15 / 20 (4 fixed options; no slider complexity)
4. **Model selector dropdown** — our unique angle; pre-populated from backend endpoint
5. **Generate button + loading state** — clear call to action with progress feedback
6. **Review screen** — numbered questions, A/B/C/D options, correct answer highlighted
7. **Clipboard copy** — formatted text, zero friction
8. **JSON download** — developer-friendly export
9. **Error handling** — bad input, API failure, empty result
10. **Empty state / example prompts** — reduce blank-page paralysis

### Defer to v1.1

- Streaming output (SSE) — improves UX but adds complexity
- Difficulty control — single prompt engineering change when ready
- Answer explanations — adds tokens and UI; clear value
- Individual question regeneration — reduces frustration on bad questions
- True/False question type — second question type is a natural v1.1 add

### Defer to v2

- URL / YouTube input
- PDF export (print-ready)
- Quiz scoring / test mode
- Collaborative features
- LMS integrations

---

## Sources

- Quizgecko quiz generator page: https://quizgecko.com/quiz-generator (HIGH confidence)
- QuizWhiz product page: https://www.quizwhiz.ai/ (HIGH confidence)
- Jotform AI Quiz Generator: https://www.jotform.com/ai/quiz-generator/ (HIGH confidence)
- involve.me AI Quiz Generator: https://www.involve.me/ai-quiz-generator (MEDIUM confidence)
- "10 Best AI Quiz Generators 2026" — involve.me blog (MEDIUM confidence, review-site sourced)
- "Best AI Quiz Maker Apps in 2026" — RemNote blog (MEDIUM confidence)
- "Best AI Quiz Generators 2026" — Edubrain (MEDIUM confidence)
- GenAI UX patterns — UX Collective: https://uxdesign.cc/20-genai-ux-patterns (MEDIUM confidence)
