/** Keep in sync with `backend/app/routers` (models list + `GenerateTextRequest`). */

import type { MultipleChoiceQuestion } from "./quiz";

export interface ModelInfo {
  id: string;
  label: string;
}

export interface GenerateTextRequest {
  topic: string;
  num_questions: number;
  model: string;
  few_shot_examples?: string[];
}

/** `POST /api/generate/question` — matches `GenerateQuestionRequest` in `routers/generate.py`. */
export interface GenerateQuestionRequest {
  model: string;
  topic: string;
  question: MultipleChoiceQuestion;
  comment?: string;
}
