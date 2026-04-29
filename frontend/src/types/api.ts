import type { MultipleChoiceQuestion } from "./quiz";

export interface ModelInfo {
  id: string;
  label: string;
}

/**
 * POST /api/generate/quiz
 * Request body for generating a quiz.
 */
export interface GenerateQuizRequest {
  topic: string;
  num_questions: number;
  model: string;
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
  comment?: string;
}
