import type { QuizResponse } from './quiz'

export type QuizMachineStatus = 'idle' | 'generating' | 'reviewing' | 'exporting' | 'error'

/** Snapshot passed into `START_GENERATE` and held on the machine; matches the topic form submit payload. */
export interface QuizFormConfig {
  topic: string
  /** Enforced client-side to match `GenerateTextRequest` / `config/quiz.ts` bounds. */
  numQuestions: number
  model: string
  /** Sent to the API only when non-empty after normalize (omit in request body if absent). */
  few_shot_examples?: string[]
}

export interface QuizMachineState {
  status: QuizMachineStatus
  formConfig: QuizFormConfig
  quiz: QuizResponse | null
  error: string | null
  /** Drives `key` on review UI so local state (e.g. export notes) resets per generation without effects. */
  reviewGeneration: number
}

export type QuizMachineAction =
  | { type: 'START_GENERATE'; payload: QuizFormConfig }
  | { type: 'GENERATE_SUCCESS'; payload: QuizResponse }
  | { type: 'GENERATE_ERROR'; payload: string }
  | { type: 'ENTER_EXPORTING' }
  | { type: 'EXIT_EXPORTING' }
  | { type: 'RESET' }
