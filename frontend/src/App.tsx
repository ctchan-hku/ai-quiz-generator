import { useQuery } from "@tanstack/react-query";
import { useState, useCallback, useEffect, type SetStateAction } from "react";
import type { LoginResponse } from "./api";
import { ErrorState } from "./components/ErrorState";
import { LoadingState } from "./components/LoadingState";
import { JournalProvider, JournalSidebar } from "./components/Journal";
import { SiteHeader } from "./components/SiteHeader";
import { TestDisplay } from "./components/TestDisplay";
import { TestForm } from "./components/TestForm";
import { MODELS_LIST_STALE_TIME_MS } from "./config/test-form";
import { useTestMachine } from "./hooks/useTestMachine";
import { getRequestErrorMessage, listModels } from "./api";
import {
  canHydrateMachine,
  cloneForLastReviewSnapshot,
  isReviewingWithPayload,
  loadPersistedSession,
  savePersistedSession,
} from "./lib/session-persistence";
import type { TestFormConfig } from "./types/test-machine";

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
    resetRefine,
  } = useTestMachine();

  const [comments, setComments] = useState(
    () => loadPersistedSession()?.comments ?? [],
  );
  const [lastReviewGeneration, setLastReviewGeneration] = useState(
    () => loadPersistedSession()?.machine.reviewGeneration ?? 0,
  );
  const [lastReview, setLastReview] = useState(
    () => loadPersistedSession()?.lastReview ?? null,
  );
  const [testFormSurfaceKey, setTestFormSurfaceKey] = useState(0);
  const [isJournalOpen, setIsJournalOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState<LoginResponse | null>(null);

  const updateFormDraft = useCallback(
    (action: SetStateAction<TestFormConfig>) => {
      dispatch({ type: "SET_FORM_CONFIG", payload: action });
    },
    [dispatch],
  );

  useEffect(() => {
    const testLength =
      state.test?.questions.length ??
      state.battle?.left.baseTestResponse.questions.length ??
      0;
    if (
      state.status !== "reviewing" ||
      state.reviewGeneration === lastReviewGeneration ||
      testLength === 0
    ) {
      return;
    }
    const id = window.setTimeout(() => {
      setComments(Array.from({ length: testLength }, () => ""));
      setLastReviewGeneration(state.reviewGeneration);
    }, 0);
    return () => window.clearTimeout(id);
  }, [
    state.status,
    state.reviewGeneration,
    state.test?.questions.length,
    state.battle?.left.baseTestResponse.questions.length,
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
      v: 6,
      machine: state,
      comments,
      lastReview,
    });
  }, [state, comments, lastReview]);

  const handleNewTest = useCallback(() => {
    if (isReviewingWithPayload(state)) {
      setLastReview(cloneForLastReviewSnapshot(state, comments));
      setTestFormSurfaceKey((k) => k + 1);
    }
    setComments([]);
    dispatch({
      type: "RESET",
      form: isReviewingWithPayload(state)
        ? structuredClone(state.formConfig)
        : undefined,
    });
  }, [state, comments, dispatch]);

  const handleViewLastTest = useCallback(() => {
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
                  onClick={handleNewTest}
                >
                  New test
                </Button>
              ) : null}
              {state.status !== "reviewing" && lastReview != null ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="shrink-0"
                  onClick={handleViewLastTest}
                  disabled={!canHydrateMachine(lastReview.machine)}
                >
                  View last test
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
          <TestForm
            key={testFormSurfaceKey}
            config={state.formConfig}
            onConfigChange={updateFormDraft}
            loggedInUser={loggedInUser}
            onLoggedInUserChange={setLoggedInUser}
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
                ? "Generating two tests…"
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
            <TestDisplay
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
          state.test &&
          state.questionVersions &&
          state.selectedVersionIndex ? (
            <TestDisplay
              mode="review"
              test={state.test}
              topic={state.formConfig.topic}
              generationForm={state.formConfig}
              models={modelsQuery.data ?? []}
              resolvedModel={state.test.model_used}
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
              refine={state.refine}
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
