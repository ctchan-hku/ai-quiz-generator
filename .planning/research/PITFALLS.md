# Domain Pitfalls: AI Quiz Generator

**Domain:** AI-powered quiz generation (FastAPI + React Vite + OpenAI-compatible API)
**Researched:** 2026-04-22
**Stack:** FastAPI (Railway) · React Vite (Vercel) · openai-hk proxy · PDF upload · anonymous users

---

## Critical Pitfalls

Mistakes that cause rewrites, runaway costs, or completely broken experiences.

---

### Pitfall 1: LLM Returns Invalid or Structurally Broken JSON

**What goes wrong:** The LLM emits JSON that fails `json.loads()` — trailing commas, unmatched brackets, truncated output, or escaped characters mid-string. Even when `response_format: json_object` is specified, the model only guarantees syntactically valid JSON, not schema adherence. The quiz frontend crashes trying to render `undefined` answer arrays.

**Why it happens:**
- `json_object` mode (JSON Mode) guarantees valid JSON syntax — not that your schema is respected.
- `json_schema` strict mode (Structured Outputs) guarantees schema compliance — but is a server-side feature only available on official OpenAI endpoints; third-party proxies like openai-hk may silently fall back to JSON Mode or return generic errors.
- Long PDFs can cause the LLM to truncate mid-response, producing broken JSON.
- Deeply nested schemas (e.g., `question → options → correctIndex → explanation`) increase failure rates.

**Consequences:** Frontend JavaScript crash; quiz is unrenderable; user gets a blank screen with no error message.

**Prevention:**
1. Always wrap LLM output in a `try/except json.JSONDecodeError` and return a structured 422 error to the frontend.
2. Use Pydantic models to validate the parsed JSON against the expected shape — not just `json.loads()`.
3. Flatten the schema: a `questions[]` array where each item has `question`, `options[]`, `correct_index`, and `explanation` is simpler and less error-prone than nested objects.
4. Set `max_tokens` explicitly (e.g., 2000 per 5-question batch) to prevent mid-token truncation.
5. Implement one automatic retry on parse failure with a corrective re-prompt: `"Your previous response was not valid JSON. Return only the JSON array with no preamble."`
6. Do **not** rely on `strict: true` from the openai-hk proxy — validate client-side with Pydantic regardless.

**Detection (warning signs):**
- Any `json.JSONDecodeError` in logs.
- Response payload starts with `"Sure! Here is your quiz:"` (model ignored JSON-only instruction).
- Response is cut off at a token boundary (`"correct_index": 2, "exp` — incomplete).

**Phase:** Address in the first LLM integration phase. Do not ship without Pydantic validation + retry logic.

---

### Pitfall 2: Scanned PDFs Return Empty Text Silently

**What goes wrong:** A user uploads a scanned PDF (photographed textbook, printed and re-scanned exam). The parser (`pypdf`, `pdfplumber`) extracts zero text — no error is raised, no exception is thrown. The LLM receives an empty or near-empty prompt and either hallucinates an entirely fabricated quiz or returns an error about insufficient context. The user sees a quiz about topics from the model's training data, not their document.

**Why it happens:** Text-based PDF parsers operate on embedded text streams in the PDF. Scanned documents contain only image bytes — there is no text layer. The parser silently returns `""` or `" "` per page.

**Consequences:** User uploads a valid document and receives a nonsensical quiz — highest trust-destroying failure mode. No error is surfaced.

**Prevention:**
1. After extraction, count words (or characters): if extracted text is fewer than 50 words total, treat the document as a scanned/image PDF and return a clear user-facing error: `"This PDF appears to be scanned. Please upload a text-based or digitally created PDF."`
2. Do **not** attempt OCR on the server as a fallback for MVP — it adds significant complexity and latency. Instead, detect and reject gracefully.
3. Expose the word count to the user before generation: `"Extracted 2,340 words from 12 pages"` so they can verify the content was read.

**Detection (warning signs):**
- Extracted text is empty or < 50 words for multi-page PDFs.
- LLM output references topics completely unrelated to the document.
- Extraction completes in < 10ms for a large PDF (no text to read).

**Phase:** Address in the PDF upload + parsing phase.

---

### Pitfall 3: Anonymous API Abuse — Runaway OpenAI Costs

**What goes wrong:** Because there is no authentication, any user (or bot) can hammer the `/generate` endpoint. Each request triggers a PDF parse + LLM call with potentially 4,000–8,000 input tokens. A single bot loop at 1 request/second consumes hundreds of dollars per hour. Real-world incidents of this type have cost developers $500+ in a single day.

**Why it happens:** No auth means no per-user tracking. Without rate limiting, the only cost control is OpenAI's own account-level hard caps, which may take hours to activate.

**Consequences:** Total account balance depleted; service suspended; API key revoked; project shut down before launch.

**Prevention:**
1. Add IP-based rate limiting on the FastAPI `/generate` endpoint from day one. `slowapi` with `get_remote_address` is the minimum acceptable default. Suggested limit: **3 requests per IP per hour**.
2. Set `max_tokens` on every LLM call — never leave it uncapped.
3. Enforce a maximum input size for PDF text before it reaches the LLM: truncate at a defined token ceiling (e.g., 6,000 tokens) and inform the user.
4. Set an OpenAI account-level **hard spending cap** (monthly limit) in the dashboard before going live.
5. Log every request with its estimated token count and cost. Alert when daily spend exceeds a threshold (e.g., $5/day).
6. Add a file size limit on upload (e.g., 10MB max) at the FastAPI level before any processing occurs.

**Detection (warning signs):**
- Identical or similar IPs appearing many times in access logs within minutes.
- OpenAI usage dashboard showing unexpectedly high token counts.
- P99 response time spikes (many concurrent LLM calls from abuse).

**Phase:** Address in the API endpoint setup phase — rate limiting must ship before any public URL is shared.

---

## Moderate Pitfalls

Issues that degrade the product significantly but can be patched without a rewrite.

---

### Pitfall 4: CORS Misconfiguration Between Railway and Vercel

**What goes wrong:** The React frontend on `*.vercel.app` makes a POST to the FastAPI backend on `*.railway.app`. The browser blocks the response with a CORS error. Because this only manifests in the deployed environment (not localhost), it often only appears during integration testing or after launch.

**Why it happens:**
- `allow_origins=["*"]` is used, but `allow_credentials=True` is also set — browsers reject this combination.
- The production Vercel URL is not added to `allow_origins` (only localhost is listed).
- `CORSMiddleware` is added after other middleware, causing it to not intercept preflight `OPTIONS` requests.

**Consequences:** Entire app is broken in production. Users see a blank error state or a browser CORS error in the console.

**Prevention:**
1. Load allowed origins from environment variables: `CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173`.
2. Never combine `allow_origins=["*"]` with `allow_credentials=True`.
3. Add `CORSMiddleware` as the **first** middleware registered in the FastAPI app.
4. Test CORS behavior explicitly against the production Vercel URL before announcing the app — use `curl -H "Origin: https://your-app.vercel.app"`.
5. Include `allow_methods=["POST", "OPTIONS"]` and `allow_headers=["Content-Type"]` explicitly.

**Detection (warning signs):**
- Browser console shows `Access-Control-Allow-Origin` header missing or mismatched.
- `OPTIONS` preflight requests returning 400 or 405.
- App works on localhost but breaks immediately on the deployed URL.

**Phase:** Address during deployment configuration phase. Environment variable setup for CORS origins should be part of the Railway/Vercel deploy checklist.

---

### Pitfall 5: Railway Cold Start Latency Destroys First Impression

**What goes wrong:** On Railway's free/hobby tier, the service spins down after inactivity. The first request after sleep can take 10–30 seconds to respond. Combined with the LLM API call (5–15 seconds), a new user's first quiz generation attempt appears to hang or time out. Most users abandon at 8–10 seconds with no feedback.

**Why it happens:** Container-based PaaS platforms with sleep-on-inactivity settings require a full container boot on the first request, including Python interpreter startup, dependency loading, and framework initialization.

**Consequences:** First-visit experience is broken. Users perceive the app as non-functional and leave.

**Prevention:**
1. Add a `/health` endpoint that returns `{"status": "ok"}` immediately with no business logic. Ping it via an uptime monitor (UptimeRobot free tier) every 5 minutes to prevent sleep.
2. Display progress feedback in the frontend immediately on form submission — do not wait for the API to respond before showing any UI change. Show a stepped loading state: `"Uploading PDF..." → "Extracting text..." → "Generating quiz..."`.
3. For the MVP, pre-warm the Railway service by including a `/health` ping in the Vercel frontend's `useEffect` on mount.
4. Keep Python dependencies lean — avoid importing large packages at module level if they are not used in the startup path.

**Detection (warning signs):**
- First request to Railway takes > 5 seconds; subsequent requests are fast.
- Railway deployment logs show container stopping after inactivity.
- Frontend `fetch()` calls time out on first load.

**Phase:** Address during deployment phase and frontend loading state implementation.

---

### Pitfall 6: Large PDFs Silently Truncated — Quiz Covers Only First Few Pages

**What goes wrong:** A user uploads a 50-page study guide. The full text is 40,000 words / ~55,000 tokens. The system either: (a) sends the full text to the LLM and hits the context window limit, causing an API error; or (b) silently truncates at an arbitrary character limit, and the LLM only sees pages 1–4. The generated quiz focuses entirely on the introduction while ignoring the core subject matter.

**Why it happens:** Without a deliberate truncation strategy, the system either passes the full extracted text or truncates at a naive byte/character limit. Neither approach provides good quiz distribution across the document.

**Consequences:** Users with long documents get misleading quizzes. The failure is invisible — no error is shown, but quiz quality is poor.

**Prevention:**
1. Count tokens using `tiktoken` before sending to the LLM. Implement a token budget (e.g., 6,000 tokens for context).
2. If the document exceeds the budget, apply **uniform sampling**: divide the document into N equal sections and sample proportionally from each, ensuring quiz coverage across the full document.
3. Tell the user how the document was handled: `"Your 47-page document was sampled evenly to fit the model's context window. Questions cover the full document."`.
4. Keep system prompt + few-shot examples compact to maximize token budget for document content.
5. For MVP, cap accepted PDFs at a stated page limit (e.g., 30 pages) rather than building complex sampling logic. Reject larger files with a clear error.

**Detection (warning signs):**
- LLM API returns `context_length_exceeded` or similar error.
- Quiz questions all reference the same page or chapter of a multi-chapter document.
- Identical quiz results regardless of which section of a large document is "important."

**Phase:** Address in the PDF parsing + LLM integration phase.

---

### Pitfall 7: Third-Party API Proxy (openai-hk) Feature Parity Gaps

**What goes wrong:** Code is written assuming OpenAI's official Structured Outputs (`response_format: {"type": "json_schema", ...}` with `strict: true`). At runtime, the openai-hk proxy either: (a) returns a generic 400/422 error on the unrecognized parameter; (b) silently ignores `strict` and falls back to basic JSON mode; or (c) routes to a model version that does not support the feature. The application breaks in production but works fine when tested against the real OpenAI API.

**Why it happens:** There is no universally enforced "OpenAI-compatible" standard. Third-party proxies implement the spec on a best-effort basis, often lagging behind new OpenAI features by weeks or months. Feature flags like `strict: true` are server-side behaviors that the proxy may simply strip.

**Consequences:** The application either crashes on generation attempts, or silently produces unvalidated output that bypasses the schema enforcement the developer expected.

**Prevention:**
1. Do not rely on the proxy to enforce JSON schema structure. Always validate LLM output with Pydantic on the FastAPI side — treat the proxy as if it only provides JSON Mode (valid JSON, no schema guarantee).
2. Test the full generation flow explicitly against openai-hk in staging before any public release. Specifically test: does the response respect your Pydantic schema? Does `response_format` cause errors?
3. Set `response_format={"type": "json_object"}` (simpler, more widely supported) rather than `json_schema` for maximum proxy compatibility.
4. Wrap the openai client call in an adapter so you can swap the base URL (official OpenAI vs. openai-hk) via environment variable — this enables direct A/B testing of the proxy.
5. Log the raw LLM response before any parsing — this surfaces proxy-specific error formats quickly.

**Detection (warning signs):**
- API returns 400/422 on generation endpoints that work against real OpenAI.
- `response_format` parameter is reflected back in error messages.
- Output varies in structure across calls despite identical prompts (schema not enforced).

**Phase:** Address in the LLM integration phase — test against the actual proxy, not just official OpenAI.

---

## Minor Pitfalls

Issues that create friction but do not break core functionality.

---

### Pitfall 8: "Frozen Spinner" — No Meaningful Loading Feedback

**What goes wrong:** The UI shows a generic spinner for the 15–30 seconds the generation takes. Users do not know if the request is in progress, queued, or has silently failed. The abandonment rate is high.

**Prevention:**
1. Break generation into client-perceivable steps with status text: `"Uploading..." → "Reading PDF..." → "Generating questions..."` using optimistic state transitions based on timing, not actual server events.
2. Show a time estimate: `"This usually takes 15–25 seconds."`.
3. Disable the submit button and show progress immediately on click — do not wait for the first API acknowledgement.

**Phase:** Address in frontend implementation phase.

---

### Pitfall 9: Multi-Column and Table-Heavy PDFs Produce Garbled Text

**What goes wrong:** PDFs with multi-column layouts (academic papers, textbooks) have text extracted in raw character order — interleaving columns. Tables are flattened into meaningless sequences of numbers. The LLM receives incoherent input and produces non-sequitur questions.

**Prevention:**
1. Use `pdfplumber` or `PyMuPDF` (`page.get_text("blocks")`) over `pypdf` for better layout handling.
2. For MVP, detect garbled extraction heuristically (very short average sentence length, high ratio of numbers to words) and warn the user: `"This PDF may have a complex layout. Quiz quality may be reduced."`
3. Do not attempt to fix multi-column extraction in the MVP — warn and ship.

**Phase:** Address in the PDF parsing phase, with a note that production-quality layout handling is a future enhancement.

---

### Pitfall 10: Hallucinated "Correct" Answers — Factually Wrong Quizzes

**What goes wrong:** The LLM marks an answer as correct that is factually wrong, or fabricates a plausible-sounding distractor that contradicts the source document. Users studying from the quiz learn incorrect information.

**Why it happens:** LLMs are probabilistic — they predict the most plausible next token, not the most accurate one. When the source text is ambiguous or the LLM's parametric knowledge conflicts with the document, it may blend both.

**Prevention:**
1. In the system prompt, instruct the model explicitly: `"All questions and correct answers MUST be derived solely from the provided text. Do not use any information outside the document."`
2. Ask the model to include the source sentence for each question: `"source_quote": "The mitochondria is the powerhouse of the cell"` — this enables downstream validation and user trust.
3. For MVP, add a disclaimer: `"Quiz generated by AI from your document. Verify answers against the source material."`
4. Do not attempt automatic answer verification via a second LLM call in MVP — the cost and latency are not justified.

**Phase:** Address in the LLM prompt engineering sub-task.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| PDF upload + parsing | Scanned PDF silent empty return | Word count guard, user-facing rejection |
| PDF parsing | Multi-column layout garbling | `pdfplumber` or PyMuPDF; quality warning |
| LLM integration | JSON parsing failure from proxy | Pydantic validation + 1 retry with corrective prompt |
| LLM integration | openai-hk proxy feature gaps | Test against actual proxy; validate client-side |
| LLM prompt design | Hallucinated correct answers | Source-only instruction in system prompt |
| Large doc handling | Silent truncation to first N pages | Token budget + uniform document sampling |
| API endpoints | Anonymous abuse / cost runaway | IP rate limiting (slowapi) before public launch |
| Deployment | CORS failure in production | Env-var-driven origins; test against prod URLs |
| Deployment | Railway cold start | Health ping keepalive; optimistic UI loading steps |
| Frontend UX | Frozen spinner abandonment | Stepped loading state with time estimate |

---

## Sources

- OpenAI Structured Outputs docs: https://developers.openai.com/api/docs/guides/structured-outputs
- OpenAI Community — Structured Outputs reliability: https://community.openai.com/t/structured-outputs-not-reliable-with-gpt-4o-mini-and-gpt-4o/918735
- PDF extraction comparison (2025): https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257
- The PDF Problem for AI: https://medium.com/@umesh382.kushwaha/the-pdf-problem-why-ai-struggles-to-read-the-documents-that-run-your-business-173673150c05
- LLM rate limiting and cost abuse: https://oneuptime.com/blog/post/2026-01-30-llm-rate-limiting/view
- Inference abuse and resource exhaustion: https://www.sourcery.ai/security/categories/inference_abuse
- Railway slow deployments: https://docs.railway.com/deployments/troubleshooting/slow-deployments
- FastAPI CORS configuration: https://davidmuraya.com/blog/fastapi-cors-configuration/
- OpenAI-compatible API quirks: https://futuresearch.ai/blog/llm-provider-quirks/
- LLM context window limits in practice: https://community.openai.com/t/processing-large-documents-128k-limit/620347
- Token management strategies: https://mohdmus99.medium.com/strategies-and-techniques-for-managing-the-size-of-the-context-window-when-using-llm-large-3c2dbc5dcc3a
- AI app UX mistakes (2026): https://www.groovyweb.co/blog/ui-mistakes-ai-apps-2026
