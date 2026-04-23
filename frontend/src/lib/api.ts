import axios, { isAxiosError } from 'axios'
import type { QuizResponse } from '../types/quiz'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? ''

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
})

export function getRequestErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const data = error.response?.data as { detail?: unknown } | undefined
    if (data?.detail !== undefined) {
      const { detail } = data
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail)) {
        return detail
          .map((item) => (typeof item === 'object' && item && 'msg' in item ? String((item as { msg: string }).msg) : String(item)))
          .join('; ')
      }
    }
    return error.message || 'Request failed'
  }
  if (error instanceof Error) return error.message
  return 'Something went wrong'
}

export interface ModelInfo {
  id: string
  label: string
}

export async function listModels(): Promise<ModelInfo[]> {
  const { data } = await api.get<{ models: ModelInfo[] }>('/api/models')
  return Array.isArray(data.models) ? data.models : []
}

export interface GenerateTextBody {
  topic: string
  num_questions: number
  model: string
}

export async function generateQuiz(topic: string, numQuestions: number, model: string): Promise<QuizResponse> {
  const body: GenerateTextBody = {
    topic,
    num_questions: numQuestions,
    model,
  }
  const { data } = await api.post<QuizResponse>('/api/generate/text', body)
  return data
}
