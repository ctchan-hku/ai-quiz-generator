/**
 * Quiz UI defaults and limits — single source of truth for the topic flow.
 * Keep numeric bounds aligned with `GenerateTextRequest` in `backend/app/routers/generate.py`.
 */

/** Matches `topic` `max_length` on the backend. */
export const TOPIC_MAX_LENGTH = 2000

/** Matches backend `num_questions` validators (`ge` / `le`). */
export const NUM_QUESTIONS_MIN = 0
export const NUM_QUESTIONS_MAX = 10

/**
 * Initial question count in the form before user interaction.
 * (The API uses a different default when the field is omitted; the SPA always sends `num_questions`.)
 */
export const DEFAULT_NUM_QUESTIONS = 5

/** Initial values shared by the lifted form state and `useQuizMachine` `initialFormConfig`. */
export const quizFormFieldDefaults: { topic: string; numQuestions: number } = {
  topic: '',
  numQuestions: DEFAULT_NUM_QUESTIONS,
}

/** Minimum height for the topic textarea (px). */
export const TOPIC_TEXTAREA_MIN_HEIGHT_PX = 120

/** TanStack Query `staleTime` for `GET /api/models`. */
export const MODELS_LIST_STALE_TIME_MS = 10 * 60_000
