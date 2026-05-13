/** Axios client (`src/lib/api.ts`). */
/** Long enough for slow LLM responses; axios would otherwise abort mid-generation. */
export const HTTP_CLIENT_TIMEOUT_MS = 120_000;

/** React Query defaults (`main.tsx`). */
export const QUERY_DEFAULT_RETRY = 1;
export const MUTATION_DEFAULT_RETRY = 0;
