import { useQuery } from '@tanstack/react-query'
import { useMemo, useState, useCallback } from 'react'
import { ErrorState } from './components/ErrorState'
import { LoadingState } from './components/LoadingState'
import { JournalProvider, JournalSidebar } from './components/Journal'
import { SiteHeader } from './components/SiteHeader'
import { QuizDisplay } from './components/QuizDisplay'
import { QuizForm } from './components/QuizForm'
import { MODELS_LIST_STALE_TIME_MS, quizFormFieldDefaults } from './config/quiz'
import { useQuizMachine } from './hooks/useQuizMachine'
import { getRequestErrorMessage, listModels } from './lib/api'

function App() {
  const {
    state,
    dispatch,
    submitGenerate,
    commitBattleWinner,
    cancelGenerate,
    cancelRefine,
    isGenerating,
    refineQuestion,
    refiningIndex,
    refineErrorIndex,
    refineErrorMessage,
    resetRefine,
  } = useQuizMachine()
  const [topic, setTopic] = useState(quizFormFieldDefaults.topic)
  const [numQuestions, setNumQuestions] = useState(quizFormFieldDefaults.numQuestions)
  /** `null`: use first model from `GET /api/models` until the user selects another. */
  const [pickedModel, setPickedModel] = useState<string | null>(null)
  const [comments, setComments] = useState<string[]>([])
  const [lastReviewGeneration, setLastReviewGeneration] = useState<number>(0)
  const [isJournalOpen, setIsJournalOpen] = useState(false)

  // Reset comments when a new quiz or battle comparison is opened
  const quizLengthForComments =
    state.quiz?.questions.length ??
    state.battle?.left.baseQuizResponse.questions.length ??
    0
  if (
    state.status === 'reviewing' &&
    state.reviewGeneration !== lastReviewGeneration &&
    quizLengthForComments > 0
  ) {
    setComments(Array.from({ length: quizLengthForComments }, () => ''))
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

  const isBattleGenerating =
    state.status === 'generating' &&
    !!state.formConfig.battle_opponent_model?.trim() &&
    state.formConfig.battle_opponent_model.trim() !==
      state.formConfig.model.trim()

  return (
    <JournalProvider>
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

        {state.status === 'generating' ? (
          <LoadingState
            headline={
              isBattleGenerating ? 'Generating two quizzes…' : undefined
            }
            toolbarRight={
              <button
                type="button"
                className="btn-secondary shrink-0 px-3 py-2 text-sm"
                onClick={cancelGenerate}
              >
                Stop
              </button>
            }
          />
        ) : null}
        {state.status === 'error' && state.error ? (
          <ErrorState error={state.error} onRetry={() => dispatch({ type: 'RESET' })} />
        ) : null}

        <main className="min-w-0">
          {state.status === 'reviewing' && state.battle ? (
            <QuizDisplay
              key={`battle-${state.reviewGeneration}`}
              mode="battle"
              battle={state.battle}
              topic={topic}
              models={modelList}
              onPickWinner={commitBattleWinner}
            />
          ) : null}
          {state.status === 'reviewing' &&
          state.quiz &&
          state.questionVersions &&
          state.selectedVersionIndex ? (
            <QuizDisplay
              mode="review"
              quiz={state.quiz}
              topic={topic}
              resolvedModel={state.quiz.model_used}
              comments={comments}
              onCommentChange={handleCommentChange}
              questionVersions={state.questionVersions}
              selectedVersionIndex={state.selectedVersionIndex}
              onSetQuestionVersion={(i, s) =>
                dispatch({ type: 'SET_QUESTION_VERSION', payload: { index: i, selected: s } })
              }
              onRefine={refineQuestion}
              onRefinePanelClose={resetRefine}
              onCancelRefine={cancelRefine}
              refiningIndex={refiningIndex}
              refineErrorIndex={refineErrorIndex}
              refineErrorMessage={refineErrorMessage}
            />
          ) : null}
        </main>

        <JournalSidebar
          isOpen={isJournalOpen}
          onClose={() => setIsJournalOpen(false)}
        />
      </div>
    </JournalProvider>
  )
}

export default App
