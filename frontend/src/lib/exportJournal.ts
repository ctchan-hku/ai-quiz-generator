import type { QuizQuestion, QuizResponse } from '../types/quiz'

export const EXPORT_JOURNAL_STORAGE_KEY = 'mastery-exec-quiz-export-journal'

export interface QuizExportQuestion {
  index: number
  question_type: string
  question: string
  explanation: string
  comment: string
  options?: string[]
  correct_indices?: number[]
}

export interface QuizExportRecord {
  exported_at: string
  topic: string
  model_used: string
  source: QuizResponse['source']
  truncated?: boolean
  questions: QuizExportQuestion[]
}

export interface ExportJournal {
  schema_version: 1
  updated_at: string
  quizzes: QuizExportRecord[]
}

function emptyJournal(): ExportJournal {
  return {
    schema_version: 1,
    updated_at: new Date().toISOString(),
    quizzes: [],
  }
}

export function loadJournal(): ExportJournal {
  try {
    const raw = localStorage.getItem(EXPORT_JOURNAL_STORAGE_KEY)
    if (raw == null || raw === '') return emptyJournal()
    const parsed = JSON.parse(raw) as unknown
    if (!parsed || typeof parsed !== 'object') return emptyJournal()
    const o = parsed as Record<string, unknown>
    if (o.schema_version !== 1 || !Array.isArray(o.quizzes)) return emptyJournal()
    return {
      schema_version: 1,
      updated_at: typeof o.updated_at === 'string' ? o.updated_at : new Date().toISOString(),
      quizzes: o.quizzes as QuizExportRecord[],
    }
  } catch {
    return emptyJournal()
  }
}

export function saveJournal(j: ExportJournal): void {
  const next: ExportJournal = {
    ...j,
    updated_at: new Date().toISOString(),
  }
  try {
    localStorage.setItem(EXPORT_JOURNAL_STORAGE_KEY, JSON.stringify(next))
  } catch (e) {
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      throw new Error('Storage full — clear the journal or free browser space.')
    }
    throw e
  }
}

export function appendQuizRecord(record: QuizExportRecord): ExportJournal {
  const j = loadJournal()
  j.quizzes.push(record)
  saveJournal(j)
  return j
}

export function clearJournal(): void {
  localStorage.removeItem(EXPORT_JOURNAL_STORAGE_KEY)
}

function toExportQuestion(q: QuizQuestion, index: number, comment: string): QuizExportQuestion {
  const trimmed = comment.trim()
  if (q.question_type === 'multiple_choice') {
    return {
      index,
      question_type: q.question_type,
      question: q.question,
      options: q.options,
      correct_indices: q.correct_indices,
      explanation: q.explanation,
      comment: trimmed,
    }
  }
  return {
    index,
    question_type: q.question_type,
    question: q.question,
    explanation: q.explanation,
    comment: trimmed,
  }
}

export function buildQuizExportRecord(params: {
  quiz: QuizResponse
  topic: string
  commentsByIndex: string[]
}): QuizExportRecord {
  const { quiz, topic, commentsByIndex } = params
  return {
    exported_at: new Date().toISOString(),
    topic: topic.trim(),
    model_used: quiz.model_used,
    source: quiz.source,
    truncated: quiz.truncated,
    questions: quiz.questions.map((q, i) =>
      toExportQuestion(q, i, commentsByIndex[i] ?? ''),
    ),
  }
}

export function downloadJournalFile(journal: ExportJournal, filename = 'quiz-export-journal.json'): void {
  const json = JSON.stringify(journal, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.rel = 'noopener'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
