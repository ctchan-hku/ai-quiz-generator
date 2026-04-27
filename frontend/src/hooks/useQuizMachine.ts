import { useMutation } from '@tanstack/react-query'
import { useCallback, useReducer } from 'react'
import { quizFormFieldDefaults } from '../config/quiz'
import { generateQuiz, generateQuestion, getRequestErrorMessage } from '../lib/api'
import type {
  QuizFormConfig,
  QuizMachineAction,
  QuizMachineState,
  RefineQuestionParams,
} from '../types/quiz-machine'
import { buildResolvedQuizResponse as buildResolved } from '../types/quiz-machine'

const initialFormConfig: QuizFormConfig = {
  topic: quizFormFieldDefaults.topic,
  numQuestions: quizFormFieldDefaults.numQuestions,
  model: '',
}

const initialState: QuizMachineState = {
  status: 'idle',
  formConfig: initialFormConfig,
  baseQuizResponse: null,
  questionVersions: null,
  selectedVersionIndex: null,
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
    case 'GENERATE_SUCCESS': {
      const questionVersions = action.payload.questions.map((q) => [q])
      const selectedVersionIndex = action.payload.questions.map(() => 0)
      return {
        ...state,
        status: 'reviewing',
        baseQuizResponse: action.payload,
        questionVersions,
        selectedVersionIndex,
        quiz: buildResolved(action.payload, questionVersions, selectedVersionIndex),
        error: null,
        reviewGeneration: state.reviewGeneration + 1,
      }
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
    case 'APPEND_QUESTION_VERSION': {
      if (
        state.status !== 'reviewing' ||
        state.baseQuizResponse == null ||
        state.questionVersions == null ||
        state.selectedVersionIndex == null
      ) {
        return state
      }
      const { index, question } = action.payload
      const newVersions = state.questionVersions.map((arr, i) =>
        i === index ? [...arr, question] : arr,
      )
      const newSelected = state.selectedVersionIndex.map((s, i) =>
        i === index ? newVersions[i].length - 1 : s,
      )
      return {
        ...state,
        questionVersions: newVersions,
        selectedVersionIndex: newSelected,
        quiz: buildResolved(state.baseQuizResponse, newVersions, newSelected),
      }
    }
    case 'SET_QUESTION_VERSION': {
      if (
        state.status !== 'reviewing' ||
        state.baseQuizResponse == null ||
        state.questionVersions == null ||
        state.selectedVersionIndex == null
      ) {
        return state
      }
      const { index, selected } = action.payload
      const slot = state.questionVersions[index]
      if (selected < 0 || selected >= slot.length) return state
      const newSelected = state.selectedVersionIndex.map((s, i) =>
        i === index ? selected : s,
      )
      return {
        ...state,
        selectedVersionIndex: newSelected,
        quiz: buildResolved(state.baseQuizResponse, state.questionVersions, newSelected),
      }
    }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

export function useQuizMachine() {
  const [state, dispatch] = useReducer(quizReducer, initialState)

  const generateMutation = useMutation({
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

  const refineMutation = useMutation({
    mutationFn: (p: RefineQuestionParams) => {
      const trimmed = p.comment.trim()
      return generateQuestion({
        model: p.model,
        topic: p.topic,
        question: p.question,
        comment: trimmed === '' ? undefined : trimmed,
      })
    },
    onSuccess: (data, variables) => {
      dispatch({
        type: 'APPEND_QUESTION_VERSION',
        payload: { index: variables.index, question: data },
      })
    },
  })

  const submitGenerate = useCallback(
    (config: QuizFormConfig) => {
      generateMutation.mutate(config)
    },
    [generateMutation],
  )

  const refineQuestion = useCallback(
    (params: RefineQuestionParams) => {
      refineMutation.mutate(params)
    },
    [refineMutation],
  )

  const resetRefine = useCallback(() => {
    refineMutation.reset()
  }, [refineMutation])

  return {
    state,
    dispatch,
    submitGenerate,
    isGenerating: generateMutation.isPending,
    refineQuestion,
    isRefining: refineMutation.isPending,
    refiningIndex: refineMutation.isPending ? refineMutation.variables?.index ?? null : null,
    refineErrorMessage:
      refineMutation.isError && refineMutation.variables != null
        ? getRequestErrorMessage(refineMutation.error)
        : null,
    refineErrorIndex:
      refineMutation.isError && refineMutation.variables != null
        ? refineMutation.variables.index
        : null,
    resetRefine,
  }
}
