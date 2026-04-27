import { useMutation } from '@tanstack/react-query'
import { useCallback, useReducer } from 'react'
import { quizFormFieldDefaults } from '../config/quiz'
import { generateQuiz, getRequestErrorMessage } from '../lib/api'
import type { QuizFormConfig, QuizMachineAction, QuizMachineState } from '../types/quiz-machine'

const initialFormConfig: QuizFormConfig = {
  topic: quizFormFieldDefaults.topic,
  numQuestions: quizFormFieldDefaults.numQuestions,
  model: '',
}

const initialState: QuizMachineState = {
  status: 'idle',
  formConfig: initialFormConfig,
  quiz: null,
  error: null,
  reviewGeneration: 0,
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
        reviewGeneration: state.reviewGeneration + 1,
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
    mutationFn: (formConfig: QuizFormConfig) => generateQuiz(formConfig),
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
