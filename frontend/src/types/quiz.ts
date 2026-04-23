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

export type QuizQuestion = MultipleChoiceQuestion

export interface QuizResponse {
  questions: QuizQuestion[]
  model_used: string
  source: 'topic' | 'file'
  truncated?: boolean
}
