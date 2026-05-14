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

export const NUM_QUESTIONS_MIN = 1;
export const NUM_QUESTIONS_MAX = 10;

/**
 * Form default only: backend defaults to 10 when `num_questions` is omitted, but the SPA always sends the field.
 */
export const DEFAULT_NUM_QUESTIONS = 1;

/** Matches backend multi-step pipeline default (`pipeline_version` 2). */
export const DEFAULT_PIPELINE_VERSION = 2 as const;

/** `[primaryModelId, opponentModelId]`; opponent is empty when not battling (`QuizFormConfig.models`). */
export const DEFAULT_MODEL_PAIR: readonly [string, string] = ["", ""];

/**
 * Single source of truth for quiz form initial values (SPA + machine `QuizFormConfig` seeds).
 * Field names match `QuizFormConfig` where overlap applies; opponent is always `models[1]`.
 */
export const quizFormFieldDefaults: {
  topic: string;
  numQuestions: number;
  pipeline_version: typeof DEFAULT_PIPELINE_VERSION;
  models: readonly [string, string];
  battleEnabled: boolean;
  few_shot_examples: readonly string[];
  user_instructions: readonly string[];
} = {
  topic: "",
  numQuestions: DEFAULT_NUM_QUESTIONS,
  pipeline_version: DEFAULT_PIPELINE_VERSION,
  models: DEFAULT_MODEL_PAIR,
  battleEnabled: false,
  few_shot_examples: [],
  user_instructions: [],
};

export const TOPIC_TEXTAREA_MIN_HEIGHT_PX = 80;
export const FEW_SHOT_TEXTAREA_MIN_HEIGHT_PX = 96;

export const MODELS_LIST_STALE_TIME_MS = 10 * 60_000;

/** Shared typography for quiz form section headings (coverage, instructions, counts, …). */
export const QUIZ_FORM_SECTION_TITLE_CLASS =
  "font-heading text-sm font-bold text-foreground";
