import { useMutation } from '@tanstack/react-query'
import { useCallback, useReducer } from 'react'
import { generateQuiz, getRequestErrorMessage } from '../lib/api'
import type { QuizResponse } from '../types/quiz'

export type QuizMachineStatus = 'idle' | 'generating' | 'reviewing' | 'exporting' | 'error'

export interface QuizFormConfig {
  topic: string
  /** Backend allows 0–10 for `/api/generate/text`. */
  numQuestions: number
  model: string
}

export interface QuizMachineState {
  status: QuizMachineStatus
  formConfig: QuizFormConfig
  quiz: QuizResponse | null
  error: string | null
}

type QuizMachineAction =
  | { type: 'START_GENERATE'; payload: QuizFormConfig }
  | { type: 'GENERATE_SUCCESS'; payload: QuizResponse }
  | { type: 'GENERATE_ERROR'; payload: string }
  | { type: 'ENTER_EXPORTING' }
  | { type: 'EXIT_EXPORTING' }
  | { type: 'RESET' }

const defaultModel = import.meta.env.VITE_DEFAULT_MODEL ?? 'gpt-4o-mini'

const initialFormConfig: QuizFormConfig = {
  topic: '',
  numQuestions: 5,
  model: defaultModel,
}

const initialState: QuizMachineState = {
  status: 'idle',
  formConfig: initialFormConfig,
  quiz: null,
  error: null,
}

function quizReducer(state: QuizMachineState, action: QuizMachineAction): QuizMachineState {
  switch (action.type) {
    case 'START_GENERATE':
      return {
        ...state,
        status: 'generating',
        formConfig: action.payload,
        error: null,
      }
    case 'GENERATE_SUCCESS':
      return {
        ...state,
        status: 'reviewing',
        quiz: action.payload,
        error: null,
      }
    case 'GENERATE_ERROR':
      return {
        ...state,
        status: 'error',
        error: action.payload,
      }
    case 'ENTER_EXPORTING':
      if (state.status !== 'reviewing') return state
      return { ...state, status: 'exporting' }
    case 'EXIT_EXPORTING':
      if (state.status !== 'exporting') return state
      return { ...state, status: 'reviewing' }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

export function useQuizMachine() {
  const [state, dispatch] = useReducer(quizReducer, initialState)

  const mutation = useMutation({
    mutationFn: ({ topic, numQuestions, model }: QuizFormConfig) => generateQuiz(topic, numQuestions, model),
    onMutate: (variables) => {
      dispatch({ type: 'START_GENERATE', payload: variables })
    },
    onSuccess: (data) => {
      dispatch({ type: 'GENERATE_SUCCESS', payload: data })
    },
    onError: (err) => {
      dispatch({ type: 'GENERATE_ERROR', payload: getRequestErrorMessage(err) })
    },
  })

  const submitGenerate = useCallback(
    (config: QuizFormConfig) => {
      mutation.mutate(config)
    },
    [mutation],
  )

  return {
    state,
    dispatch,
    submitGenerate,
    isGenerating: mutation.isPending,
  }
}
