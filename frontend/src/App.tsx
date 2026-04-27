import { useQuery } from '@tanstack/react-query'
import { useMemo, useState, useCallback } from 'react'
import { ErrorState } from './components/ErrorState'
import { LoadingState } from './components/LoadingState'
import { JournalSidebar } from './components/JournalSidebar'
import { SiteHeader } from './components/SiteHeader'
import { QuizDisplay } from './components/QuizDisplay'
import { QuizForm } from './components/QuizForm'
import { MODELS_LIST_STALE_TIME_MS, quizFormFieldDefaults } from './config/quiz'
import { useQuizMachine } from './hooks/useQuizMachine'
import { getRequestErrorMessage, listModels } from './lib/api'

function App() {
  const { state, dispatch, submitGenerate, isGenerating } = useQuizMachine()
  const [topic, setTopic] = useState(quizFormFieldDefaults.topic)
  const [numQuestions, setNumQuestions] = useState(quizFormFieldDefaults.numQuestions)
  /** `null`: use first model from `GET /api/models` until the user selects another. */
  const [pickedModel, setPickedModel] = useState<string | null>(null)
  const [comments, setComments] = useState<string[]>([])
  const [lastReviewGeneration, setLastReviewGeneration] = useState<number>(0)
  const [isJournalOpen, setIsJournalOpen] = useState(false)

  // Reset comments when a new quiz is generated
  if (state.status === 'reviewing' && state.reviewGeneration !== lastReviewGeneration && state.quiz) {
    setComments(state.quiz.questions.map(() => ""))
    setLastReviewGeneration(state.reviewGeneration)
  }

  const handleCommentChange = useCallback((index: number, value: string) => {
    setComments((prev) => {
      const next = [...prev]
      next[index] = value
      return next
    })
  }, [])

  const modelsQuery = useQuery({
    queryKey: ['models'],
    queryFn: listModels,
    staleTime: MODELS_LIST_STALE_TIME_MS,
  })

  const modelList = useMemo(() => modelsQuery.data ?? [], [modelsQuery.data])

  const resolvedModel = useMemo(() => {
    if (!modelList.length) return ''
    if (pickedModel != null && modelList.some((m) => m.id === pickedModel)) return pickedModel
    return modelList[0].id
  }, [modelList, pickedModel])

  const modelsErrorMessage =
    modelsQuery.isError ? getRequestErrorMessage(modelsQuery.error) : null

  return (
    <div className="mx-auto flex min-h-svh max-w-7xl flex-col gap-6 px-4 py-8 md:px-6 lg:px-8 lg:py-10">
      <SiteHeader
        trailing={
          <button
            type="button"
            className="btn-secondary shrink-0 px-3 py-2 text-sm"
            onClick={() => setIsJournalOpen(true)}
          >
            Journal
          </button>
        }
      />

      <QuizForm
        topic={topic}
        onTopicChange={setTopic}
        numQuestions={numQuestions}
        onNumQuestionsChange={setNumQuestions}
        model={resolvedModel}
        onModelChange={setPickedModel}
        models={modelList}
        modelsLoading={modelsQuery.isLoading}
        modelsError={modelsErrorMessage}
        isLoading={isGenerating}
        onSubmit={submitGenerate}
      />

      {state.status === 'generating' ? <LoadingState /> : null}
      {state.status === 'error' && state.error ? (
        <ErrorState error={state.error} onRetry={() => dispatch({ type: 'RESET' })} />
      ) : null}

      <main className="min-w-0">
        {state.status === 'reviewing' && state.quiz ? (
          <QuizDisplay
            quiz={state.quiz}
            topic={topic}
            comments={comments}
            onCommentChange={handleCommentChange}
          />
        ) : null}
      </main>

      <JournalSidebar
        isOpen={isJournalOpen}
        onClose={() => setIsJournalOpen(false)}
      />
    </div>
  )
}

export default App
