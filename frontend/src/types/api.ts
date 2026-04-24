/** Keep in sync with `backend/app/routers` (models list + `GenerateTextRequest`). */

export interface ModelInfo {
  id: string;
  label: string;
}

export interface GenerateTextRequest {
  topic: string;
  num_questions: number;
  model: string;
}
