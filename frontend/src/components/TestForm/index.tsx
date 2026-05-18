import { testFormFieldDefaults } from "../../config/test-form";
import type { TestFormConfig } from "../../types/test-machine";
import type { ModelInfo } from "../../api";
import type { Dispatch, SetStateAction } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FewShotExamplesSection } from "./FewShotExamplesSection";
import { UserInstructionsSection } from "./UserInstructionsSection";
import { BattleModeSwitch } from "./BattleModeSwitch";
import { ModelBoard } from "./ModelBoard";
import { NumberOfQuestionsField } from "./NumberOfQuestionsField";
import { PipelineVersionSection } from "./PipelineVersionSection";
import { TopicField } from "./TopicField";
import { getNextOpponentId } from "@/lib/modelBoard";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

export interface TestFormProps {
  config: TestFormConfig;
  onConfigChange: Dispatch<SetStateAction<TestFormConfig>>;
  /** Catalog from `GET /api/models`. */
  availableModels: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  onSubmit: (config: TestFormConfig) => void;
  isLoading: boolean;
}

export function TestForm({
  config,
  onConfigChange,
  availableModels,
  modelsLoading,
  modelsError,
  onSubmit,
  isLoading,
}: TestFormProps) {
  const {
    topic,
    numQuestions,
    pipeline_version,
    few_shot_examples,
    user_instructions,
    models,
    battleEnabled,
  } = config;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      ...config,
      models: battleEnabled
        ? [models[0], models[1]]
        : [models[0], testFormFieldDefaults.models[1]],
      few_shot_examples: [...few_shot_examples],
      user_instructions: [...user_instructions],
    });
  }

  const submitLabel = battleEnabled ? "Generate battle" : "Generate test";

  return (
    <Card size="sm">
      <CardContent className="pt-0">
        <form className="text-left" onSubmit={handleSubmit}>
          <TopicField
            topic={topic}
            onTopicChange={(t) =>
              onConfigChange((prev) => ({ ...prev, topic: t }))
            }
            isLoading={isLoading}
          />

          <UserInstructionsSection
            user_instructions={user_instructions}
            onUserInstructionsChange={(action) =>
              onConfigChange((prev) => ({
                ...prev,
                user_instructions:
                  typeof action === "function"
                    ? action(prev.user_instructions)
                    : action,
              }))
            }
            isLoading={isLoading}
          />

          <div className="mb-4">
            <NumberOfQuestionsField
              numQuestions={numQuestions}
              onNumQuestionsChange={(n) =>
                onConfigChange((prev) => ({ ...prev, numQuestions: n }))
              }
              isLoading={isLoading}
            />
          </div>

          <PipelineVersionSection
            value={pipeline_version}
            onChange={(v) =>
              onConfigChange((prev) => ({ ...prev, pipeline_version: v }))
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
                    for your summary and refinements.
                  </p>
                </div>
                <BattleModeSwitch
                  checked={battleEnabled}
                  labelledBy="battle-mode-intro"
                  disabled={isLoading}
                  onCheckedChange={(next) => {
                    onConfigChange((s) =>
                      next
                        ? {
                            ...s,
                            battleEnabled: true,
                            models: [
                              s.models[0],
                              getNextOpponentId(s.models[0], availableModels),
                            ],
                          }
                        : {
                            ...s,
                            battleEnabled: false,
                            models: [
                              s.models[0],
                              testFormFieldDefaults.models[1],
                            ],
                          },
                    );
                  }}
                />
              </div>
            </fieldset>

            {!battleEnabled ? (
              <ModelBoard
                model={models[0]}
                onModelChange={(id) =>
                  onConfigChange((prev) => ({
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
                    onConfigChange((prev) => ({
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
                    onConfigChange((prev) => ({
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

          <FewShotExamplesSection
            few_shot_examples={few_shot_examples}
            onFewShotExamplesChange={(action) =>
              onConfigChange((prev) => ({
                ...prev,
                few_shot_examples:
                  typeof action === "function"
                    ? action(prev.few_shot_examples)
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
