/**
 * Keep bounds aligned with `backend/app/features/generation/config/prompts.py` and the test router.
 */

import type { TestFormConfig } from "../types/test-machine";

export const TOPIC_MAX_LENGTH = 2000;

/** Aligned with `FEW_SHOT_MAX_*` in generation `prompts.py`. */
export const FEW_SHOT_MAX_COUNT = 3;
export const FEW_SHOT_MAX_LENGTH = 2000;

/** Matches `USER_INSTRUCTION_*` in generation `prompts.py`. */
export const USER_INSTRUCTIONS_MAX_COUNT = 5;
export const USER_INSTRUCTION_MAX_LENGTH = 400;

export const NUM_QUESTIONS_MIN = 1;
export const NUM_QUESTIONS_MAX = 10;

export const DEFAULT_NUM_QUESTIONS = 1;
export const DEFAULT_PIPELINE_VERSION = 2 as const;

/** Label for UI / summaries; matches wording in PipelineVersionSection (`Version 1` / `Version 2`). */
export function pipelineVersionCaption(version: 1 | 2): string {
  return `Version ${version}`;
}

/** Default `TestFormConfig` for new sessions / machine reset (`structuredClone` when a fresh mutable copy is required). */
export const testFormFieldDefaults: TestFormConfig = {
  topic: "",
  numQuestions: DEFAULT_NUM_QUESTIONS,
  pipeline_version: DEFAULT_PIPELINE_VERSION,
  models: ["", ""],
  battleEnabled: false,
  few_shot_examples: [],
  user_instructions: [],
  selected_test_ids: [],
};

export const TOPIC_TEXTAREA_MIN_HEIGHT_PX = 80;
export const FEW_SHOT_TEXTAREA_MIN_HEIGHT_PX = 96;

export const MODELS_LIST_STALE_TIME_MS = 10 * 60_000;
