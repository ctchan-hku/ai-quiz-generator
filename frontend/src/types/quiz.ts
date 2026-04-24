/**
 * Mirrors the multiple-choice slice of `backend/app/models/schemas.py` (`BaseQuestion` → `OptionsQuestion` → `MultipleChoiceQuestion`).
 * v1 SPA only models and handles this variant.
 */

export type QuizSource = "topic" | "file";

export interface BaseQuestion {
  question_type: string;
  question: string;
  explanation: string;
}

export interface OptionsQuestion extends BaseQuestion {
  options: string[];
  correct_indices: number[];
}

export interface MultipleChoiceQuestion extends OptionsQuestion {
  question_type: "multiple_choice";
}

export interface QuizResponse {
  questions: MultipleChoiceQuestion[];
  model_used: string;
  source: QuizSource;
  truncated?: boolean;
}
