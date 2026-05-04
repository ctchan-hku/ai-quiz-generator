import type { MultipleChoiceQuestion, QuizResponse, QuizSource } from './quiz'

/** Bump when the persisted JSON shape changes; `loadJournal` drops data from older versions. */
export const EXPORT_JOURNAL_SCHEMA_VERSION = 2 as const

export type ExportJournalSchemaVersion = typeof EXPORT_JOURNAL_SCHEMA_VERSION

/** One question as it appears in the downloaded JSON: full item plus order index and optional user notes. */
export type ExportedQuizQuestion = MultipleChoiceQuestion & { index: number; comment: string }

export interface QuizExportRecord {
  exported_at: string
  topic: string
  model_used: string
  cost_usd: number
  source: QuizSource
  truncated?: boolean
  questions: ExportedQuizQuestion[]
}

export interface ExportJournal {
  schema_version: ExportJournalSchemaVersion
  updated_at: string
  quizzes: QuizExportRecord[]
}

export type BuildQuizExportRecordParams = {
  quiz: QuizResponse
  topic: string
  commentsByIndex: string[]
}
