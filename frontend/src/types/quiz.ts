/** Mirrors backend `MultipleChoiceQuestion` / `QuizResponse` for v1 topic flow. */

export interface QuestionBase {
  question: string
  explanation: string
}

export interface MultipleChoiceQuestion extends QuestionBase {
  question_type: 'multiple_choice'
  options: string[]
  correct_indices: number[]
}

/** v1 UI renders only `multiple_choice`; other variants exist on the API for forward compatibility. */
export type QuizQuestion =
  | MultipleChoiceQuestion
  | { question_type: 'true_false' | 'multi_select' | 'short_answer'; question: string; explanation: string }

export interface QuizResponse {
  questions: QuizQuestion[]
  model_used: string
  source: 'topic' | 'file'
  truncated?: boolean
}
