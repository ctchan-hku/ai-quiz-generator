import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { EmptyState } from './components/EmptyState'
import { ErrorState } from './components/ErrorState'
import { LoadingState } from './components/LoadingState'
import { QuizDisplay } from './components/QuizDisplay'
import { QuizForm } from './components/QuizForm'
import { MODELS_LIST_STALE_TIME_MS, quizFormFieldDefaults } from './config/quiz'
import { useQuizMachine } from './hooks/useQuizMachine'
import { getRequestErrorMessage, listModels } from './lib/api'

function App() {
  const { state, dispatch, submitGenerate, isGenerating } = useQuizMachine()
  const [topic, setTopic] = useState(quizFormFieldDefaults.topic)
  const [numQuestions, setNumQuestions] = useState(quizFormFieldDefaults.numQuestions)
  /** `null` = default to first model from API until the user picks one. */
  const [pickedModel, setPickedModel] = useState<string | null>(null)

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
    <main className="mx-auto flex min-h-svh max-w-4xl flex-col gap-6 px-4 py-8 md:px-6 lg:px-8 lg:py-10">
      <header className="text-left">
        <h1 className="mt-0 mb-2 font-[family-name:var(--font-heading)] text-3xl font-semibold text-[var(--color-text)] md:text-4xl">
          AI Quiz Generator
        </h1>
        <p className="mb-0 text-base text-[var(--color-text)] opacity-85">
          Turn a topic into a multiple-choice quiz — academic style preview.
        </p>
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

      {state.status === 'idle' ? <EmptyState onAutoFill={setTopic} /> : null}
      {state.status === 'generating' ? <LoadingState /> : null}
      {state.status === 'reviewing' && state.quiz ? <QuizDisplay quiz={state.quiz} /> : null}
      {state.status === 'error' && state.error ? (
        <ErrorState error={state.error} onRetry={() => dispatch({ type: 'RESET' })} />
      ) : null}
    </main>
  )
}

export default App
