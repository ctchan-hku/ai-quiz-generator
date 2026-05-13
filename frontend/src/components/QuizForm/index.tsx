import { useState, type SetStateAction } from "react";
import {
  FEW_SHOT_MAX_COUNT,
  FEW_SHOT_MAX_LENGTH,
  QUIZ_FORM_SECTION_TITLE_CLASS,
  USER_INSTRUCTION_LINE_MAX_CHARS,
  USER_INSTRUCTIONS_MAX,
  quizFormFieldDefaults,
} from "../../config/quiz";
import type { QuizFormConfig } from "../../types/quiz-machine";
import type { ModelInfo } from "../../types/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FewShotExamplesSection } from "./FewShotExamplesSection";
import { UserInstructionsLinesSection } from "./UserInstructionsLinesSection";
import { BattleModeSwitch } from "./BattleModeSwitch";
import { ModelBoard } from "./ModelBoard";
import { NumberOfQuestionsField } from "./NumberOfQuestionsField";
import { PipelineVersionSection } from "./PipelineVersionSection";
import { TopicField } from "./TopicField";
import { getNextOpponentId } from "@/lib/modelBoard";

export interface QuizFormProps {
  topic: string;
  onTopicChange: (topic: string) => void;
  numQuestions: number;
  onNumQuestionsChange: (n: number) => void;
  model: string;
  onModelChange: (model: string | null) => void;
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  onSubmit: (config: QuizFormConfig) => void;
  isLoading: boolean;
  /** Filled when `QuizForm` remounts after "New quiz"; restores pipeline, examples, battle, etc. */
  restoreConfig: QuizFormConfig | null;
}

export function QuizForm({
  topic,
  onTopicChange,
  numQuestions,
  onNumQuestionsChange,
  model,
  onModelChange,
  models,
  modelsLoading,
  modelsError,
  onSubmit,
  isLoading,
  restoreConfig,
}: QuizFormProps) {
  const [localError, setLocalError] = useState<string | null>(null);
  const [extras, setExtras] = useState(() => localFormSeed(restoreConfig));
  const {
    pipelineVersion,
    exampleRows,
    userInstructionLines,
    battleEnabled,
    battleDefaultOpponentId,
  } = extras;
  /** Right Opponent explicit choice; `null` uses `battleDefaultOpponentId`. */
  const [opponentOverrideId, setOpponentOverrideId] = useState<string | null>(
    null,
  );

  const displayedRightOpponentId =
    opponentOverrideId ?? battleDefaultOpponentId;

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
    if (!models.length) {
      setLocalError("No models are available. Check backend AVAILABLE_MODELS.");
      return;
    }
    if (!model.trim()) {
      setLocalError("Select a model.");
      return;
    }

    if (battleEnabled) {
      if (models.length < 2) {
        setLocalError("Battle mode needs at least two configured models.");
        return;
      }
      const rightModelId = (opponentOverrideId ?? battleDefaultOpponentId).trim();
      if (!rightModelId) {
        setLocalError(
          "Pick a Right Opponent model — none is available as a default alternate.",
        );
        return;
      }
      if (rightModelId === model.trim()) {
        setLocalError(
          "Pick two different models — Left Opponent and Right Opponent must differ.",
        );
        return;
      }
    }

    const fewShotNormalized: string[] = [];
    for (const row of exampleRows) {
      const t = row.trim();
      if (!t) {
        continue;
      }
      if (t.length > FEW_SHOT_MAX_LENGTH) {
        setLocalError(
          `Each example must be at most ${FEW_SHOT_MAX_LENGTH} characters.`,
        );
        return;
      }
      fewShotNormalized.push(t);
    }
    if (fewShotNormalized.length > FEW_SHOT_MAX_COUNT) {
      setLocalError(`At most ${FEW_SHOT_MAX_COUNT} examples are allowed.`);
      return;
    }

    const trimmed = topic.trim();
    if (!trimmed && fewShotNormalized.length === 0) {
      setLocalError("Enter a topic or add at least one example.");
      return;
    }

    const userInstructionsNormalized: string[] = [];
    for (const row of userInstructionLines) {
      const t = row.trim();
      if (!t) {
        continue;
      }
      if (t.length > USER_INSTRUCTION_LINE_MAX_CHARS) {
        setLocalError(
          `Each instruction line must be at most ${USER_INSTRUCTION_LINE_MAX_CHARS} characters.`,
        );
        return;
      }
      userInstructionsNormalized.push(t);
    }
    if (userInstructionsNormalized.length > USER_INSTRUCTIONS_MAX) {
      setLocalError(
        `At most ${USER_INSTRUCTIONS_MAX} user instruction lines are allowed.`,
      );
      return;
    }

    const base: QuizFormConfig = {
      topic: trimmed,
      numQuestions,
      model,
      pipeline_version: pipelineVersion,
    };
    if (battleEnabled) {
      base.battle_opponent_model = (
        opponentOverrideId ?? battleDefaultOpponentId
      ).trim();
    }
    if (fewShotNormalized.length > 0) {
      base.few_shot_examples = fewShotNormalized;
    }
    if (userInstructionsNormalized.length > 0) {
      base.user_instructions = userInstructionsNormalized;
    }
    onSubmit(base);
  }

  const submitDisabled =
    isLoading || modelsLoading || !!modelsError || models.length === 0;

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

          <UserInstructionsLinesSection
            lines={userInstructionLines}
            onLinesChange={(action) =>
              setExtras((e) => ({
                ...e,
                userInstructionLines: resolveAction(
                  e.userInstructionLines,
                  action,
                ),
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
            value={pipelineVersion}
            onChange={(v) => setExtras((e) => ({ ...e, pipelineVersion: v }))}
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
                    if (next) {
                      setOpponentOverrideId(null);
                    }
                    setExtras((s) => ({
                      ...s,
                      battleEnabled: next,
                      ...(next
                        ? {
                            battleDefaultOpponentId: getNextOpponentId(
                              model.trim(),
                              models,
                            ),
                          }
                        : {}),
                    }));
                  }}
                />
              </div>
            </fieldset>

            {!battleEnabled ? (
              <ModelBoard
                model={model}
                onModelChange={onModelChange}
                models={models}
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
                  models={models}
                  modelsLoading={modelsLoading}
                  modelsError={modelsError}
                  isLoading={isLoading}
                  boardRole="battle-left"
                />
                <ModelBoard
                  model={displayedRightOpponentId}
                  onModelChange={setOpponentOverrideId}
                  models={models}
                  modelsLoading={modelsLoading}
                  modelsError={modelsError}
                  isLoading={isLoading}
                  boardRole="battle-right"
                />
              </div>
            )}
          </div>

          <FewShotExamplesSection
            exampleRows={exampleRows}
            onExampleRowsChange={(action) =>
              setExtras((e) => ({
                ...e,
                exampleRows: resolveAction(e.exampleRows, action),
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
  return typeof action === "function"
    ? (action as (p: T) => T)(prev)
    : action;
}

function localFormSeed(r: QuizFormConfig | null) {
  const opponent = (r?.battle_opponent_model ?? "").trim();
  return {
    pipelineVersion: r?.pipeline_version ?? quizFormFieldDefaults.pipelineVersion,
    exampleRows: [...(r?.few_shot_examples ?? [])],
    userInstructionLines: [...(r?.user_instructions ?? [])],
    battleEnabled: opponent.length > 0,
    battleDefaultOpponentId: opponent,
  };
}
