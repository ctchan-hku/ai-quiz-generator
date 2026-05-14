import { useQuery } from "@tanstack/react-query";
import { useMemo, useState, useCallback, useEffect, useRef } from "react";
import { ErrorState } from "./components/ErrorState";
import { LoadingState } from "./components/LoadingState";
import { JournalProvider, JournalSidebar } from "./components/Journal";
import { SiteHeader } from "./components/SiteHeader";
import { QuizDisplay } from "./components/QuizDisplay";
import { QuizForm } from "./components/QuizForm";
import {
  MODELS_LIST_STALE_TIME_MS,
  quizFormFieldDefaults,
} from "./config/quiz-form";
import { useQuizMachine } from "./hooks/useQuizMachine";
import { getRequestErrorMessage, listModels } from "./api";
import {
  canHydrateMachine,
  cloneForLastReviewSnapshot,
  isReviewingWithPayload,
  loadPersistedSession,
  savePersistedSession,
} from "./lib/session-persistence";
import type { QuizFormConfig } from "./types/quiz-machine";

import { Button } from "./components/ui/button";

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
  } = useQuizMachine();
  const [topic, setTopic] = useState(
    () => loadPersistedSession()?.topic ?? quizFormFieldDefaults.topic,
  );
  const [numQuestions, setNumQuestions] = useState(
    () =>
      loadPersistedSession()?.numQuestions ??
      quizFormFieldDefaults.numQuestions,
  );
  /** `null`: use the first model from `GET /api/models` until the user picks another. */
  const [pickedModel, setPickedModel] = useState<string | null>(
    () => loadPersistedSession()?.pickedModel ?? null,
  );
  const [comments, setComments] = useState(
    () => loadPersistedSession()?.comments ?? [],
  );
  const [lastReviewGeneration, setLastReviewGeneration] = useState(
    () => loadPersistedSession()?.machine.reviewGeneration ?? 0,
  );
  const [lastReview, setLastReview] = useState(
    () => loadPersistedSession()?.lastReview ?? null,
  );
  /** Remount `QuizForm` after "New quiz"; ref keeps restore payload across Strict Mode. */
  const quizFormRestoreRef = useRef<QuizFormConfig | null>(null);
  const [quizFormSurfaceKey, setQuizFormSurfaceKey] = useState(0);
  const [isJournalOpen, setIsJournalOpen] = useState(false);

  // Reset comments when a new quiz or battle comparison is opened
  const quizLengthForComments =
    state.quiz?.questions.length ??
    state.battle?.left.baseQuizResponse.questions.length ??
    0;
  if (
    state.status === "reviewing" &&
    state.reviewGeneration !== lastReviewGeneration &&
    quizLengthForComments > 0
  ) {
    setComments(Array.from({ length: quizLengthForComments }, () => ""));
    setLastReviewGeneration(state.reviewGeneration);
  }

  const handleCommentChange = useCallback((index: number, value: string) => {
    setComments((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  }, []);

  useEffect(() => {
    savePersistedSession({
      v: 2,
      machine: state,
      topic,
      numQuestions,
      pickedModel,
      comments,
      lastReview,
    });
  }, [state, topic, numQuestions, pickedModel, comments, lastReview]);

  const handleNewQuiz = useCallback(() => {
    if (isReviewingWithPayload(state)) {
      setLastReview(
        cloneForLastReviewSnapshot(state, topic, comments, pickedModel),
      );
      quizFormRestoreRef.current = structuredClone(state.formConfig);
      setQuizFormSurfaceKey((k) => k + 1);
    }
    setComments([]);
    dispatch({ type: "RESET" });
  }, [state, topic, comments, pickedModel, dispatch]);

  const handleViewLastQuiz = useCallback(() => {
    if (lastReview == null || !canHydrateMachine(lastReview.machine)) {
      return;
    }
    dispatch({ type: "HYDRATE", payload: lastReview.machine });
    setTopic(lastReview.topic);
    setNumQuestions(lastReview.machine.formConfig.numQuestions);
    setPickedModel(lastReview.pickedModel);
    setComments([...lastReview.comments]);
    setLastReviewGeneration(lastReview.machine.reviewGeneration);
  }, [lastReview, dispatch]);

  const modelsQuery = useQuery({
    queryKey: ["models"],
    queryFn: listModels,
    staleTime: MODELS_LIST_STALE_TIME_MS,
  });

  const modelList = useMemo(() => modelsQuery.data ?? [], [modelsQuery.data]);

  const resolvedModel = useMemo(() => {
    if (!modelList.length) return "";
    if (pickedModel != null && modelList.some((m) => m.id === pickedModel)) {
      return pickedModel;
    }
    return modelList[0].id;
  }, [modelList, pickedModel]);

  const isReviewing = state.status === "reviewing";
  const modelsErrorMessage = modelsQuery.isError
    ? getRequestErrorMessage(modelsQuery.error)
    : null;

  const isBattleGenerating =
    state.status === "generating" &&
    !!state.formConfig.battle_opponent_model?.trim() &&
    state.formConfig.battle_opponent_model.trim() !==
      state.formConfig.model.trim();

  return (
    <JournalProvider>
      <div className="mx-auto flex min-h-svh max-w-5xl flex-col gap-4 px-4 pt-4 pb-8 md:gap-5 md:px-8 md:pb-10">
        <SiteHeader
          trailing={
            <div className="flex shrink-0 flex-wrap items-center justify-end gap-2">
              {isReviewing ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="shrink-0"
                  onClick={handleNewQuiz}
                >
                  New quiz
                </Button>
              ) : null}
              {!isReviewing && lastReview != null ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="shrink-0"
                  onClick={handleViewLastQuiz}
                  disabled={!canHydrateMachine(lastReview.machine)}
                >
                  View last quiz
                </Button>
              ) : null}
              <Button
                variant="outline"
                size="sm"
                className="shrink-0"
                onClick={() => setIsJournalOpen(true)}
              >
                Journal
              </Button>
            </div>
          }
        />

        {!isReviewing ? (
          <QuizForm
            key={quizFormSurfaceKey}
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
            restoreConfig={quizFormRestoreRef.current}
          />
        ) : null}

        {state.status === "generating" ? (
          <LoadingState
            headline={
              isBattleGenerating ? "Generating two quizzes…" : undefined
            }
            toolbarRight={
              <Button
                variant="destructive"
                size="sm"
                className="shrink-0"
                onClick={cancelGenerate}
              >
                Stop
              </Button>
            }
          />
        ) : null}
        {state.status === "error" && state.error ? (
          <ErrorState
            error={state.error}
            onRetry={() => dispatch({ type: "RESET" })}
          />
        ) : null}

        <main className="min-w-0">
          {state.status === "reviewing" && state.battle ? (
            <QuizDisplay
              key={`battle-${state.reviewGeneration}`}
              mode="battle"
              battle={state.battle}
              topic={topic}
              models={modelList}
              onPickWinner={commitBattleWinner}
            />
          ) : null}
          {state.status === "reviewing" &&
          state.quiz &&
          state.questionVersions &&
          state.selectedVersionIndex ? (
            <QuizDisplay
              mode="review"
              quiz={state.quiz}
              topic={topic}
              generationForm={state.formConfig}
              models={modelList}
              resolvedModel={state.quiz.model_used}
              comments={comments}
              onCommentChange={handleCommentChange}
              questionVersions={state.questionVersions}
              selectedVersionIndex={state.selectedVersionIndex}
              onSetQuestionVersion={(i, s) =>
                dispatch({
                  type: "SET_QUESTION_VERSION",
                  payload: { index: i, selected: s },
                })
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
          models={modelList}
        />
      </div>
    </JournalProvider>
  );
}

export default App;
