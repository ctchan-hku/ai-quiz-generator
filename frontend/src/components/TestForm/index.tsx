import { testFormFieldDefaults } from "@/config/test-form";
import type { TestFormConfig } from "@/config/test-form";
import type { LoginResponse, ModelInfo } from "@/api/contracts";
import type { Dispatch, SetStateAction } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FewShotExamplesSection } from "./FewShotExamplesSection";
import { UserWorkspaceSection } from "@/components/workspace/UserWorkspaceSection";
import { UserInstructionsSection } from "./UserInstructionsSection";
import { BattleModeSwitch } from "./BattleModeSwitch";
import { ModelBoard } from "./ModelBoard";
import { NumberOfQuestionsField } from "./NumberOfQuestionsField";
import { PipelineVersionSection } from "./PipelineVersionSection";
import { TopicField } from "./TopicField";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

export interface TestFormProps {
  formConfig: TestFormConfig;
  onFormConfigChange: Dispatch<SetStateAction<TestFormConfig>>;
  onBattleModeChange: (enabled: boolean) => void;
  loggedInUser: LoginResponse | null;
  onLoggedInUserChange: (user: LoginResponse | null) => void;
  /** Catalog from `GET /api/models`. */
  availableModels: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  onSubmit: (formConfig: TestFormConfig) => void;
  isLoading: boolean;
}

export function TestForm({
  formConfig,
  onFormConfigChange,
  loggedInUser,
  onLoggedInUserChange,
  availableModels,
  modelsLoading,
  modelsError,
  onSubmit,
  isLoading,
  onBattleModeChange,
}: TestFormProps) {
  const {
    topic,
    numQuestions,
    pipelineVersion,
    fewShotExamples,
    userInstructions,
    models,
    battleEnabled,
  } = formConfig;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      ...formConfig,
      models: battleEnabled
        ? [models[0], models[1]]
        : [models[0], testFormFieldDefaults.models[1]],
      fewShotExamples: [...fewShotExamples],
      userInstructions: [...userInstructions],
    });
  }

  const submitLabel = battleEnabled ? "Generate battle" : "Generate test";

  return (
    <Card size="sm" className="overflow-visible">
      <CardContent className="overflow-visible pt-0">
        <form className="text-left" onSubmit={handleSubmit}>
          <TopicField
            topic={topic}
            onTopicChange={(t) =>
              onFormConfigChange((prev) => ({ ...prev, topic: t }))
            }
            isLoading={isLoading}
          />

          <UserInstructionsSection
            userInstructions={userInstructions}
            onUserInstructionsChange={(action) =>
              onFormConfigChange((prev) => ({
                ...prev,
                userInstructions:
                  typeof action === "function"
                    ? action(prev.userInstructions)
                    : action,
              }))
            }
            isLoading={isLoading}
          />

          <div className="mb-4">
            <NumberOfQuestionsField
              numQuestions={numQuestions}
              onNumQuestionsChange={(n) =>
                onFormConfigChange((prev) => ({ ...prev, numQuestions: n }))
              }
              isLoading={isLoading}
            />
          </div>

          <PipelineVersionSection
            value={pipelineVersion}
            onChange={(v) =>
              onFormConfigChange((prev) => ({ ...prev, pipelineVersion: v }))
            }
            isLoading={isLoading}
          />

          <div className="mb-4 space-y-4">
            <fieldset className="mb-4 min-w-0 border-0 p-0">
              <legend className="sr-only">Generation mode</legend>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                <div id="battle-mode-intro" className="min-w-0 flex-1">
                  <TestFormSectionTitle as="p" className="m-0">
                    Battle Mode
                  </TestFormSectionTitle>
                  <p className="mt-1.5 mb-0 text-xs leading-relaxed text-muted-foreground">
                    Generate the same test twice with Left Opponent and Right
                    Opponent side by side in the test view, then pick the winner
                    for your summary and question edits.
                  </p>
                </div>
                <BattleModeSwitch
                  checked={battleEnabled}
                  labelledBy="battle-mode-intro"
                  disabled={isLoading}
                  onCheckedChange={onBattleModeChange}
                />
              </div>
            </fieldset>

            {!battleEnabled ? (
              <ModelBoard
                model={models[0]}
                onModelChange={(id) =>
                  onFormConfigChange((prev) => ({
                    ...prev,
                    models: [id ?? "", prev.models[1]],
                  }))
                }
                models={availableModels}
                modelsLoading={modelsLoading}
                modelsError={modelsError}
                isLoading={isLoading}
                boardRole="standard"
              />
            ) : (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 lg:gap-8 lg:items-start">
                <ModelBoard
                  model={models[0]}
                  onModelChange={(id) =>
                    onFormConfigChange((prev) => ({
                      ...prev,
                      models: [id ?? "", prev.models[1]],
                    }))
                  }
                  models={availableModels}
                  modelsLoading={modelsLoading}
                  modelsError={modelsError}
                  isLoading={isLoading}
                  boardRole="battle-left"
                />
                <ModelBoard
                  model={models[1]}
                  onModelChange={(id) =>
                    onFormConfigChange((prev) => ({
                      ...prev,
                      models: [prev.models[0], id ?? ""],
                    }))
                  }
                  models={availableModels}
                  modelsLoading={modelsLoading}
                  modelsError={modelsError}
                  isLoading={isLoading}
                  boardRole="battle-right"
                />
              </div>
            )}
          </div>
        </form>

        <form className="text-left" onSubmit={handleSubmit}>
          <FewShotExamplesSection
            fewShotExamples={fewShotExamples}
            onFewShotExamplesChange={(action) =>
              onFormConfigChange((prev) => ({
                ...prev,
                fewShotExamples:
                  typeof action === "function"
                    ? action(prev.fewShotExamples)
                    : action,
              }))
            }
            isLoading={isLoading}
          />

          <UserWorkspaceSection
            loggedInUser={loggedInUser}
            onLoggedInUserChange={onLoggedInUserChange}
            selectedTestIds={formConfig.selectedTestIds}
            onSelectedTestIdsChange={(action) =>
              onFormConfigChange((prev) => ({
                ...prev,
                selectedTestIds:
                  typeof action === "function"
                    ? action(prev.selectedTestIds)
                    : action,
              }))
            }
            isLoading={isLoading}
          />

          <Button
            type="submit"
            className="w-full sm:w-auto"
            disabled={isLoading}
          >
            {isLoading ? "Generating…" : submitLabel}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
