/**
 * Topic-flow limits and defaults.
 * Keep bounds aligned with `backend/app/modules/generation/config/prompts.py` and the quiz router.
 */

export const TOPIC_MAX_LENGTH = 2000;

/** Aligned with `FEW_SHOT_MAX_*` in generation `prompts.py`. */
export const FEW_SHOT_MAX_COUNT = 3;
export const FEW_SHOT_MAX_LENGTH = 2000;

/** Matches `USER_INSTRUCTION_*` in generation `prompts.py`. */
export const USER_INSTRUCTIONS_MAX = 5;
/** Per-line cap (each list item is a single `<input type="text">` row). */
export const USER_INSTRUCTION_LINE_MAX_CHARS = 400;

export const NUM_QUESTIONS_MIN = 0;
export const NUM_QUESTIONS_MAX = 10;

/**
 * Form default only: backend defaults to 10 when `num_questions` is omitted, but the SPA always sends the field.
 */
export const DEFAULT_NUM_QUESTIONS = 5;

/** Matches backend multi-step pipeline default (`pipeline_version` 2). */
export const DEFAULT_PIPELINE_VERSION = 2 as const;

export const quizFormFieldDefaults: {
  topic: string;
  numQuestions: number;
  pipelineVersion: typeof DEFAULT_PIPELINE_VERSION;
} = {
  topic: "",
  numQuestions: DEFAULT_NUM_QUESTIONS,
  pipelineVersion: DEFAULT_PIPELINE_VERSION,
};

export const TOPIC_TEXTAREA_MIN_HEIGHT_PX = 80;
export const FEW_SHOT_TEXTAREA_MIN_HEIGHT_PX = 96;

export const MODELS_LIST_STALE_TIME_MS = 10 * 60_000;
