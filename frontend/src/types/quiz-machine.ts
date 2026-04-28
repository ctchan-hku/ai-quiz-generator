import type { MultipleChoiceQuestion, QuizResponse } from './quiz'

export type QuizMachineStatus = 'idle' | 'generating' | 'reviewing' | 'exporting' | 'error'

/** Snapshot passed into `START_GENERATE` and held on the machine; matches the topic form submit payload. */
export interface QuizFormConfig {
  topic: string
  /** Enforced client-side to match `GenerateQuizRequest` / `config/quiz.ts` bounds. */
  numQuestions: number
  model: string
  /** Sent to the API only when non-empty after normalize (omit in request body if absent). */
  few_shot_examples?: string[]
  /** Optional short lines merged into MCQ schema instructions on the server. */
  user_instructions?: string[]
}

export interface QuizMachineState {
  status: QuizMachineStatus
  formConfig: QuizFormConfig
  /** First full-quiz `POST /api/generate/quiz` response; `model_used` / `source` / `truncated` stay fixed for the session. */
  baseQuizResponse: QuizResponse | null
  /** Per-question version stacks (non-empty while reviewing after a successful generate). */
  questionVersions: MultipleChoiceQuestion[][] | null
  selectedVersionIndex: number[] | null
  /** Resolved quiz: `questions[i]` = `questionVersions[i][selectedVersionIndex[i]]` for export and display. */
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
  | { type: 'APPEND_QUESTION_VERSION'; payload: { index: number; question: MultipleChoiceQuestion } }
  | { type: 'SET_QUESTION_VERSION'; payload: { index: number; selected: number } }

/** Arguments for `POST /api/generate/question` from the review UI (resolved MCQ + form `topic` / `model`). */
export interface RefineQuestionParams {
  index: number
  question: MultipleChoiceQuestion
  comment: string
  model: string
  topic: string
}

export function buildResolvedQuizResponse(
  base: QuizResponse,
  questionVersions: MultipleChoiceQuestion[][],
  selectedVersionIndex: number[],
): QuizResponse {
  return {
    model_used: base.model_used,
    source: base.source,
    truncated: base.truncated,
    questions: questionVersions.map((vers, i) => vers[selectedVersionIndex[i]]),
  }
}
