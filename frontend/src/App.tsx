import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import type { LoginResponse } from "./api";
import { ErrorState } from "./components/ErrorState";
import { LoadingState } from "./components/LoadingState";
import { JournalProvider, JournalSidebar } from "./components/Journal";
import { SiteHeader } from "./components/SiteHeader";
import { TestDisplay } from "./components/TestDisplay";
import { TestForm } from "./components/TestForm";
import { MODELS_LIST_STALE_TIME_MS } from "./config/test-form";
import { useAppSession } from "./hooks/useAppSession";
import { useTestMachine } from "./hooks/useTestMachine";
import { getRequestErrorMessage, listModels } from "./api";
import { canHydrateMachine } from "./lib/test-machine/persistence";

import { Button } from "./components/ui/button";

function App() {
  const {
    state,
    dispatch,
    submitGenerate,
    commitBattleWinner,
    cancelGenerate,
    cancelQuestionEdit,
    isGenerating,
    editQuestion,
    clearQuestionEdit,
  } = useTestMachine();

  const {
    comments,
    lastReview,
    testFormSurfaceKey,
    handleCommentChange,
    handleNewTest,
    handleViewLastTest,
    updateFormDraft,
  } = useAppSession({ state, dispatch });

  const [isJournalOpen, setIsJournalOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState<LoginResponse | null>(null);

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
              key={`battle-${state.reviewEpoch}`}
              mode="battle"
              battle={state.battle}
              topic={state.formConfig.topic}
              pipelineVersion={state.formConfig.pipelineVersion}
              models={modelsQuery.data ?? []}
              onPickWinner={commitBattleWinner}
            />
          ) : null}
          {state.status === "reviewing" && state.review ? (
            <TestDisplay
              mode="review"
              topic={state.formConfig.topic}
              generationForm={state.formConfig}
              models={modelsQuery.data ?? []}
              comments={comments}
              onCommentChange={handleCommentChange}
              review={state.review}
              onSetQuestionVersion={(i, s) =>
                dispatch({
                  type: "SET_QUESTION_VERSION",
                  payload: { index: i, selected: s },
                })
              }
              onEditQuestion={editQuestion}
              onQuestionEditClose={clearQuestionEdit}
              onCancelQuestionEdit={cancelQuestionEdit}
              questionEdit={state.questionEdit}
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
