import type { MultipleChoiceQuestion } from "./quiz";

/** USD per 1M tokens (Phase 10 `GET /api/models` contract). */
export interface ModelPrice {
  input: number | null;
  output: number | null;
}

export interface ModelInfo {
  id: string;
  label: string;
  price: ModelPrice;
}

/**
 * POST /api/generate/quiz
 * Request body for generating a quiz.
 */
export interface GenerateQuizRequest {
  topic: string;
  num_questions: number;
  model: string;
  /** 1 = single-call full quiz; 2 = multi-step pipeline (default). */
  pipeline_version?: 1 | 2;
  few_shot_examples?: string[];
  user_instructions?: string[];
}

/**
 * POST /api/generate/question
 * Request body for generating or refining a question.
 */
export interface GenerateQuestionRequest {
  model: string;
  topic: string;
  question: MultipleChoiceQuestion;
  /** Trimmed on send */
  comment: string;
}
