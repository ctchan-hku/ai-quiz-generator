import { useState } from "react";
import type { LoginResponse } from "@/api/contracts";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { JournalSidebar } from "@/components/Journal";
import { useJournal } from "@/hooks/useJournal";
import { SiteHeader } from "@/components/SiteHeader";
import { TestDisplay } from "@/components/TestDisplay";
import { TestForm } from "@/components/TestForm";
import { useAppSession } from "@/hooks/useAppSession";
import { useBattleModeToggle } from "@/hooks/useBattleModeToggle";
import { useModels } from "@/hooks/useModels";
import { useRestoreWorkspace } from "@/hooks/useRestoreWorkspace";
import { useTestMachine } from "@/hooks/useTestMachine";
import { Button } from "@/components/ui/button";

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
    canViewLastTest,
  } = useAppSession({ state, dispatch });

  const { models, isLoading: modelsLoading, error: modelsError } = useModels();

  const [isJournalOpen, setIsJournalOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState<LoginResponse | null>(null);
  useRestoreWorkspace(setLoggedInUser);
  const journal = useJournal(models);
  const { onBattleModeChange } = useBattleModeToggle({
    onFormConfigChange: updateFormDraft,
    availableModels: models,
  });

  return (
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
                disabled={!canViewLastTest}
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
          formConfig={state.formConfig}
          onFormConfigChange={updateFormDraft}
          onBattleModeChange={onBattleModeChange}
          loggedInUser={loggedInUser}
          onLoggedInUserChange={setLoggedInUser}
          availableModels={models}
          modelsLoading={modelsLoading}
          modelsError={modelsError}
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
            models={models}
            onPickWinner={commitBattleWinner}
          />
        ) : null}
        {state.status === "reviewing" && state.review ? (
          <TestDisplay
            mode="review"
            topic={state.formConfig.topic}
            formConfig={state.formConfig}
            models={models}
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
        {...journal}
      />
    </div>
  );
}

export default App;
