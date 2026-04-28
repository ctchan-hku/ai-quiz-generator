/**
 * Matches `backend/app/models/schemas.py` (`MultipleChoiceQuestion`) — only MCQ supported.
 * Validation counts: `backend/app/models/mcq_constraints.py`.
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
}
