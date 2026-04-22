# Phase 2: AI Generation Pipeline - Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

The backend service that accepts a text topic, calls the LLM to generate multiple-choice questions, validates the JSON response, handles errors/retries, and enforces rate limits.

**In scope:**
- `POST /api/generate/text` endpoint
- Pydantic schema validation for discriminated union
- Prompt builder and OpenAI async client configuration
- Automatic retry on JSON/Pydantic validation failure
- Rate limiting via `slowapi`

**Out of scope:**
- File uploads (Phase 4)
- React frontend (Phase 3)
- Models other than `multiple_choice`
- Custom difficulty levels
</domain>

<decisions>
## Implementation Decisions

### Rate Limit Error Message
- **D-01:** When the 3 requests/IP/hour limit is hit, return a specific helpful message ("You've hit the limit of 3 quizzes per hour. Please wait [X] minutes.") to improve UX for anonymous users rather than a generic 429 message.

### Claude's Discretion
- The exact prompt phrasing for the AI generator (as long as it enforces the required schema).
- The internal structure of the `slowapi` integration and error handling middleware.
- Logging verbosity for generation failures.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — vision, constraints, out-of-scope decisions
- `.planning/REQUIREMENTS.md` — full requirement list (BACK-04, BACK-06, AI-01, AI-02, AI-03, AI-04, AI-05)

### Architecture
- `.planning/research/ARCHITECTURE.md` § `API Endpoint Design` — payload shapes, validation constraints
- `.planning/research/ARCHITECTURE.md` § `Prompt Engineering` — system prompt rules, retry logic, error handling
- `.planning/research/ARCHITECTURE.md` § `Rate Limiting` — `slowapi` setup, IP retrieval

### Prior Phases
- `.planning/phases/01-backend-scaffold/01-CONTEXT.md` — backend layout, environment variable structure, CORS configuration

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/config.py`: Exposes `settings.openai_api_key` and `settings.openai_base_url` for the OpenAI client.
- `backend/app/main.py`: Where the new `routers/generate.py` will be registered, and `slowapi` will be configured.

### Established Patterns
- Environment variables are loaded via `pydantic-settings` in `config.py`.
- Routing uses `APIRouter` in the `routers/` directory.

### Integration Points
- `backend/app/routers/generate.py` will be created to house `POST /api/generate/text`.
- `slowapi` middleware will be added to `backend/app/main.py`.

</code_context>

<specifics>
## Specific Ideas

- The LLM client uses `AsyncOpenAI(base_url="https://api.openai-hk.com/v1", api_key=settings.openai_api_key)`.
- Use `response_format={"type": "json_object"}`.
- Max tokens set to 4096 and timeout to 55s.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-ai-generation-pipeline*
*Context gathered: 2026-04-22*
