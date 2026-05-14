/**
 * HTTP JSON shapes shared with the FastAPI backend (`app/modules/generation`).
 * Includes successful response bodies — those types are contracts with the wire format
 * and are reused across UI state for the same reason.
 */

/** USD per 1M tokens (`GET /api/models`). */
export interface ModelPrice {
  input: number | null;
  output: number | null;
}

export interface ModelInfo {
  id: string;
  label: string;
  price: ModelPrice;
}

/** POST /api/generate/quiz */
export interface GenerateQuizRequest {
  topic: string;
  num_questions: number;
  model: string;
  /** 1 = single-call full quiz; 2 = multi-step pipeline (default). */
  pipeline_version: 1 | 2;
  few_shot_examples: string[];
  user_instructions: string[];
}

/**
 * Matches `backend/app/modules/generation/models/mc_question.py` (`MultipleChoiceQuestion`).
 * Counts: `backend/app/modules/generation/config/mc_question.py` and `frontend/src/constants/mc_question.ts`.
 */
export interface MultipleChoiceQuestion {
  question_type: "multiple_choice";
  question: string;
  options: string[];
  correct_indices: number[];
  explanation: string;
}

/** POST /api/generate/question */
export interface GenerateQuestionRequest {
  model: string;
  topic: string;
  question: MultipleChoiceQuestion;
  /** Trimmed on send */
  comment: string;
}

export type QuizSource = "topic" | "file";

/** Successful body from POST /api/generate/quiz (`QuizResponse` on the server). */
export interface QuizResponse {
  questions: MultipleChoiceQuestion[];
  model_used: string;
  source: QuizSource;
  cost_usd: number;
}

/** Successful body from POST /api/generate/question (wrapper). */
export interface QuestionGenerateResponse {
  question: MultipleChoiceQuestion;
  cost_usd: number;
}
