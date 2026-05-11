/**
 * Matches `backend/app/modules/generation/models/mc_question.py` (`MultipleChoiceQuestion`).
 * Counts: `backend/app/modules/generation/config/mc_question.py` and `frontend/src/constants/mc_question.ts`.
 */

export type QuizSource = "topic" | "file";

export interface MultipleChoiceQuestion {
  question_type: "multiple_choice";
  question: string;
  options: string[];
  correct_indices: number[];
  explanation: string;
}

export interface QuizResponse {
  questions: MultipleChoiceQuestion[];
  model_used: string;
  source: QuizSource;
  truncated?: boolean;
  cost_usd: number;
}

/** POST /api/generate/question success body (wrapper). */
export interface QuestionGenerateResponse {
  question: MultipleChoiceQuestion;
  cost_usd: number;
}
