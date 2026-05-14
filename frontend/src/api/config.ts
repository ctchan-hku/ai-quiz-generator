/** Axios client (`src/api/client.ts`). */
/** Long enough for slow multi-step LLM generation; axios aborts when this is exceeded. */
export const HTTP_CLIENT_TIMEOUT_MS = 600_000;

/** React Query defaults (`main.tsx`). */
export const QUERY_DEFAULT_RETRY = 1;
export const MUTATION_DEFAULT_RETRY = 0;
