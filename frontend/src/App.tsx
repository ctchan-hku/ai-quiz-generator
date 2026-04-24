import { useQuery } from '@tanstack/react-query'
import { useMemo, useState, useCallback, useEffect } from 'react'
import { ErrorState } from './components/ErrorState'
import { LoadingState } from './components/LoadingState'
import { JournalSidebar } from './components/JournalSidebar'
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
  const [isMobileJournalOpen, setIsMobileJournalOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Detect mobile viewport
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768) // Tailwind's md breakpoint is 768px
    }
    window.addEventListener('resize', handleResize)
    handleResize() // Set initial value
    return () => window.removeEventListener('resize', handleResize)
  }, [])

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
    <div className="mx-auto flex min-h-svh max-w-7xl flex-col gap-6 px-4 py-8 md:flex-row md:px-6 lg:px-8 lg:py-10">
      <main className="flex flex-1 flex-col gap-6 min-w-0">
        <header className="flex items-start justify-between gap-4 text-left">
          <div>
            <h1 className="mt-0 mb-2 font-[family-name:var(--font-heading)] text-3xl font-semibold text-[var(--color-text)] md:text-4xl">
              AI Quiz Generator
            </h1>
            <p className="mb-0 text-base text-[var(--color-text)] opacity-85">
              Turn a topic into a multiple-choice quiz — academic style preview.
            </p>
          </div>
          {isMobile ? (
            <button
              type="button"
              className="btn-secondary shrink-0 px-3 py-2 text-sm"
              onClick={() => setIsMobileJournalOpen(true)}
            >
              Journal
            </button>
          ) : null}
        </header>

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
        {state.status === 'reviewing' && state.quiz ? (
          <QuizDisplay
            quiz={state.quiz}
            topic={topic}
            comments={comments}
            onCommentChange={handleCommentChange}
          />
        ) : null}
        {state.status === 'error' && state.error ? (
          <ErrorState error={state.error} onRetry={() => dispatch({ type: 'RESET' })} />
        ) : null}
      </main>

      <JournalSidebar 
        quiz={state.status === 'reviewing' ? state.quiz : null} 
        topic={topic} 
        comments={comments} 
        isOpen={isMobileJournalOpen}
        onClose={() => setIsMobileJournalOpen(false)}
      />
    </div>
  )
}

export default App
