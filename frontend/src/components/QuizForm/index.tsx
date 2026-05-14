import { useState, type SetStateAction } from "react";
import {
  QUIZ_FORM_SECTION_TITLE_CLASS,
  quizFormFieldDefaults,
} from "../../config/quiz-form";
import type { QuizFormConfig } from "../../types/quiz-machine";
import type { ModelInfo } from "../../api";
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

/** Local fields that mirror `QuizFormConfig`; `battleEnabled` is UI-only until submit clears `models[1]` when off. */
type QuizFormLocalState = Pick<
  QuizFormConfig,
  "pipeline_version" | "few_shot_examples" | "user_instructions" | "models"
> & {
  battleEnabled: boolean;
};

export interface QuizFormProps {
  topic: string;
  onTopicChange: (topic: string) => void;
  numQuestions: number;
  onNumQuestionsChange: (n: number) => void;
  /** Primary model id (`QuizFormConfig.models[0]` on submit — not duplicated in lazy state beyond `extras.models`). */
  model: string;
  onModelChange: (model: string | null) => void;
  /** Catalog from `GET /api/models`. */
  availableModels: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  onSubmit: (config: QuizFormConfig) => void;
  isLoading: boolean;
  restoreConfig: QuizFormConfig | null;
}

export function QuizForm({
  topic,
  onTopicChange,
  numQuestions,
  onNumQuestionsChange,
  model,
  onModelChange,
  availableModels,
  modelsLoading,
  modelsError,
  onSubmit,
  isLoading,
  restoreConfig,
}: QuizFormProps) {
  const [localError, setLocalError] = useState<string | null>(null);
  const [extras, setExtras] = useState<QuizFormLocalState>(() =>
    localFormSeed(restoreConfig),
  );

  const {
    pipeline_version,
    few_shot_examples,
    user_instructions,
    models,
    battleEnabled,
  } = extras;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLocalError(null);
    if (modelsLoading) {
      setLocalError("Still loading models from the server.");
      return;
    }
    if (modelsError) {
      setLocalError("Fix the model list error above before generating.");
      return;
    }
    if (!availableModels.length) {
      setLocalError("No models are available. Check backend AVAILABLE_MODELS.");
      return;
    }
    if (!model.trim()) {
      setLocalError("Select a model.");
      return;
    }

    if (battleEnabled) {
      if (availableModels.length < 2) {
        setLocalError("Battle mode needs at least two configured models.");
        return;
      }
      const opponentId = models[1].trim();
      if (!opponentId) {
        setLocalError(
          "Pick a Right Opponent model — none is available as a default alternate.",
        );
        return;
      }
      if (opponentId === model.trim()) {
        setLocalError(
          "Pick two different models — Left Opponent and Right Opponent must differ.",
        );
        return;
      }
    }

    onSubmit({
      topic,
      numQuestions,
      models: battleEnabled
        ? [model.trim(), models[1].trim()]
        : [model.trim(), ""],
      pipeline_version,
      few_shot_examples: [...few_shot_examples],
      user_instructions: [...user_instructions],
    });
  }

  const submitDisabled =
    isLoading || modelsLoading || !!modelsError || availableModels.length === 0;

  const submitLabel = battleEnabled ? "Generate battle" : "Generate Quiz";

  return (
    <Card size="sm">
      <CardContent className="pt-0">
        <form className="text-left" onSubmit={handleSubmit}>
          <TopicField
            topic={topic}
            onTopicChange={onTopicChange}
            isLoading={isLoading}
          />

          <UserInstructionsSection
            user_instructions={user_instructions}
            onUserInstructionsChange={(action) =>
              setExtras((e) => ({
                ...e,
                user_instructions: resolveAction(e.user_instructions, action),
              }))
            }
            isLoading={isLoading}
          />

          <div className="mb-4">
            <NumberOfQuestionsField
              numQuestions={numQuestions}
              onNumQuestionsChange={onNumQuestionsChange}
              isLoading={isLoading}
            />
          </div>

          <PipelineVersionSection
            value={pipeline_version}
            onChange={(v) => setExtras((e) => ({ ...e, pipeline_version: v }))}
            isLoading={isLoading}
          />

          <div className="mb-4 space-y-4">
            <fieldset className="mb-4 min-w-0 border-0 p-0">
              <legend className="sr-only">Generation mode</legend>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                <div id="battle-mode-intro" className="min-w-0 flex-1">
                  <p className={`m-0 ${QUIZ_FORM_SECTION_TITLE_CLASS}`}>
                    Battle Mode
                  </p>
                  <p className="mt-1.5 mb-0 text-xs leading-relaxed text-muted-foreground">
                    Generate the same quiz twice with Left Opponent and Right
                    Opponent side by side in the quiz view, then pick the winner
                    for your summary and refinements.
                  </p>
                </div>
                <BattleModeSwitch
                  checked={battleEnabled}
                  labelledBy="battle-mode-intro"
                  disabled={isLoading}
                  onCheckedChange={(next) => {
                    setExtras((s) =>
                      next
                        ? {
                            ...s,
                            battleEnabled: true,
                            models: [
                              model,
                              getNextOpponentId(model.trim(), availableModels),
                            ] as [string, string],
                          }
                        : {
                            ...s,
                            battleEnabled: false,
                            models: [
                              model,
                              quizFormFieldDefaults.models[1],
                            ] as [string, string],
                          },
                    );
                  }}
                />
              </div>
            </fieldset>

            {!battleEnabled ? (
              <ModelBoard
                model={model}
                onModelChange={onModelChange}
                models={availableModels}
                modelsLoading={modelsLoading}
                modelsError={modelsError}
                isLoading={isLoading}
                boardRole="standard"
              />
            ) : (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 lg:gap-8 lg:items-start">
                <ModelBoard
                  model={model}
                  onModelChange={onModelChange}
                  models={availableModels}
                  modelsLoading={modelsLoading}
                  modelsError={modelsError}
                  isLoading={isLoading}
                  boardRole="battle-left"
                />
                <ModelBoard
                  model={models[1]}
                  onModelChange={(id) =>
                    setExtras((e) => ({
                      ...e,
                      models: [model, id ?? ""] as [string, string],
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
              setExtras((e) => ({
                ...e,
                few_shot_examples: resolveAction(e.few_shot_examples, action),
              }))
            }
            isLoading={isLoading}
          />

          {localError ? (
            <p className="mb-3 text-sm text-destructive" role="alert">
              {localError}
            </p>
          ) : null}

          <Button
            type="submit"
            className="w-full sm:w-auto"
            disabled={submitDisabled}
          >
            {isLoading ? "Generating…" : submitLabel}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function resolveAction<T>(prev: T, action: SetStateAction<T>): T {
  return typeof action === "function" ? (action as (p: T) => T)(prev) : action;
}

function localFormSeed(
  restoreConfig: QuizFormConfig | null,
): QuizFormLocalState {
  if (restoreConfig == null) {
    return {
      pipeline_version: quizFormFieldDefaults.pipeline_version,
      few_shot_examples: [...quizFormFieldDefaults.few_shot_examples],
      user_instructions: [...quizFormFieldDefaults.user_instructions],
      models: [
        quizFormFieldDefaults.models[0],
        quizFormFieldDefaults.models[1],
      ],
      battleEnabled: quizFormFieldDefaults.battleEnabled,
    };
  }
  return {
    pipeline_version: restoreConfig.pipeline_version,
    few_shot_examples: [...restoreConfig.few_shot_examples],
    user_instructions: [...restoreConfig.user_instructions],
    models: [restoreConfig.models[0], restoreConfig.models[1]],
    battleEnabled: restoreConfig.models[1].trim().length > 0,
  };
}
