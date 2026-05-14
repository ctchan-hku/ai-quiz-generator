import { useQuery } from "@tanstack/react-query";
import { useState, useCallback, useEffect, type SetStateAction } from "react";
import { ErrorState } from "./components/ErrorState";
import { LoadingState } from "./components/LoadingState";
import { JournalProvider, JournalSidebar } from "./components/Journal";
import { SiteHeader } from "./components/SiteHeader";
import { QuizDisplay } from "./components/QuizDisplay";
import { QuizForm } from "./components/QuizForm";
import { MODELS_LIST_STALE_TIME_MS } from "./config/quiz-form";
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

  const [comments, setComments] = useState(
    () => loadPersistedSession()?.comments ?? [],
  );
  const [lastReviewGeneration, setLastReviewGeneration] = useState(
    () => loadPersistedSession()?.machine.reviewGeneration ?? 0,
  );
  const [lastReview, setLastReview] = useState(
    () => loadPersistedSession()?.lastReview ?? null,
  );
  const [quizFormSurfaceKey, setQuizFormSurfaceKey] = useState(0);
  const [isJournalOpen, setIsJournalOpen] = useState(false);

  const updateFormDraft = useCallback((action: SetStateAction<QuizFormConfig>) => {
    dispatch({ type: "SET_FORM_CONFIG", payload: action });
  }, [dispatch]);

  useEffect(() => {
    const quizLength =
      state.quiz?.questions.length ??
      state.battle?.left.baseQuizResponse.questions.length ??
      0;
    if (
      state.status !== "reviewing" ||
      state.reviewGeneration === lastReviewGeneration ||
      quizLength === 0
    ) {
      return;
    }
    const id = window.setTimeout(() => {
      setComments(Array.from({ length: quizLength }, () => ""));
      setLastReviewGeneration(state.reviewGeneration);
    }, 0);
    return () => window.clearTimeout(id);
  }, [
    state.status,
    state.reviewGeneration,
    state.quiz?.questions.length,
    state.battle?.left.baseQuizResponse.questions.length,
    lastReviewGeneration,
  ]);

  const handleCommentChange = useCallback((index: number, value: string) => {
    setComments((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  }, []);

  useEffect(() => {
    savePersistedSession({
      v: 5,
      machine: state,
      comments,
      lastReview,
    });
  }, [state, comments, lastReview]);

  const handleNewQuiz = useCallback(() => {
    if (isReviewingWithPayload(state)) {
      setLastReview(cloneForLastReviewSnapshot(state, comments));
      setQuizFormSurfaceKey((k) => k + 1);
    }
    setComments([]);
    dispatch({
      type: "RESET",
      form: isReviewingWithPayload(state)
        ? structuredClone(state.formConfig)
        : undefined,
    });
  }, [state, comments, dispatch]);

  const handleViewLastQuiz = useCallback(() => {
    if (lastReview == null || !canHydrateMachine(lastReview.machine)) {
      return;
    }
    dispatch({
      type: "HYDRATE",
      payload: structuredClone(lastReview.machine),
    });
    setComments([...lastReview.comments]);
    setLastReviewGeneration(lastReview.machine.reviewGeneration);
  }, [lastReview, dispatch]);

  const modelsQuery = useQuery({
    queryKey: ["models"],
    queryFn: listModels,
    staleTime: MODELS_LIST_STALE_TIME_MS,
  });

  return (
    <JournalProvider>
      <div className="mx-auto flex min-h-svh max-w-5xl flex-col gap-4 px-4 pt-4 pb-8 md:gap-5 md:px-8 md:pb-10">
        <SiteHeader
          trailing={
            <div className="flex shrink-0 flex-wrap items-center justify-end gap-2">
              {state.status === "reviewing" ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="shrink-0"
                  onClick={handleNewQuiz}
                >
                  New quiz
                </Button>
              ) : null}
              {state.status !== "reviewing" && lastReview != null ? (
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

        {state.status !== "reviewing" ? (
          <QuizForm
            key={quizFormSurfaceKey}
            config={state.formConfig}
            onConfigChange={updateFormDraft}
            availableModels={modelsQuery.data ?? []}
            modelsLoading={modelsQuery.isLoading}
            modelsError={
              modelsQuery.isError
                ? getRequestErrorMessage(modelsQuery.error)
                : null
            }
            isLoading={isGenerating}
            onSubmit={submitGenerate}
          />
        ) : null}

        {state.status === "generating" ? (
          <LoadingState
            headline={
              state.status === "generating" &&
              state.formConfig.battleEnabled &&
              state.formConfig.models[1].trim() !== "" &&
              state.formConfig.models[1].trim() !==
                state.formConfig.models[0].trim()
                ? "Generating two quizzes…"
                : undefined
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
              topic={state.formConfig.topic}
              pipelineVersion={state.formConfig.pipeline_version}
              models={modelsQuery.data ?? []}
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
              topic={state.formConfig.topic}
              generationForm={state.formConfig}
              models={modelsQuery.data ?? []}
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
          models={modelsQuery.data ?? []}
        />
      </div>
    </JournalProvider>
  );
}

export default App;
