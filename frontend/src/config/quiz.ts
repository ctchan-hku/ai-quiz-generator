/**
 * Topic-flow limits and defaults.
 * Keep `TOPIC_MAX_LENGTH` / question bounds aligned with `GenerateTextRequest` in `backend/app/routers/generate.py`.
 */

export const TOPIC_MAX_LENGTH = 2000

export const NUM_QUESTIONS_MIN = 0
export const NUM_QUESTIONS_MAX = 10

/**
 * Form default only: backend defaults to 10 when `num_questions` is omitted, but the SPA always sends the field.
 */
export const DEFAULT_NUM_QUESTIONS = 5

export const quizFormFieldDefaults: { topic: string; numQuestions: number } = {
  topic: '',
  numQuestions: DEFAULT_NUM_QUESTIONS,
}

export const TOPIC_TEXTAREA_MIN_HEIGHT_PX = 120

export const MODELS_LIST_STALE_TIME_MS = 10 * 60_000
