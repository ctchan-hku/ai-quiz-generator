import { useMemo, useState } from "react";
import {
  FEW_SHOT_MAX_COUNT,
  FEW_SHOT_MAX_LENGTH,
  USER_INSTRUCTION_LINE_MAX_CHARS,
  USER_INSTRUCTIONS_MAX,
} from "../../config/quiz";
import type { QuizFormConfig } from "../../types/quiz-machine";
import type { ModelInfo } from "../../types/api";
import { FewShotExamplesSection } from "./FewShotExamplesSection";
import { UserInstructionsLinesSection } from "./UserInstructionsLinesSection";
import { BattleModeSwitch } from "./BattleModeSwitch";
import { ModelBoard } from "./ModelBoard";
import { NumberOfQuestionsField } from "./NumberOfQuestionsField";
import { TopicField } from "./TopicField";

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
}

function pickDefaultOpponentId(primaryId: string, list: ModelInfo[]) {
  return list.find((m) => m.id !== primaryId)?.id ?? "";
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
}: QuizFormProps) {
  const [localError, setLocalError] = useState<string | null>(null);
  const [exampleRows, setExampleRows] = useState<string[]>([]);
  const [userInstructionLines, setUserInstructionLines] = useState<string[]>(
    [],
  );
  const [battleEnabled, setBattleEnabled] = useState(false);
  /** Right Opponent explicit choice; `null` shows the suggested alternate until the user selects. */
  const [opponentOverrideId, setOpponentOverrideId] = useState<string | null>(
    null,
  );

  const defaultOpponentId = useMemo(
    () => pickDefaultOpponentId(model, models),
    [model, models],
  );

  const displayedRightOpponentId = opponentOverrideId ?? defaultOpponentId;

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
      const rightModelId = (
        opponentOverrideId ??
        defaultOpponentId ??
        ""
      ).trim();
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
    };
    if (battleEnabled) {
      base.battle_opponent_model = (
        opponentOverrideId ??
        defaultOpponentId ??
        ""
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
    <form className="card text-left" onSubmit={handleSubmit}>
      <TopicField
        topic={topic}
        onTopicChange={onTopicChange}
        isLoading={isLoading}
      />

      <UserInstructionsLinesSection
        lines={userInstructionLines}
        onLinesChange={setUserInstructionLines}
        isLoading={isLoading}
      />

      <div className="mb-4">
        <NumberOfQuestionsField
          numQuestions={numQuestions}
          onNumQuestionsChange={onNumQuestionsChange}
          isLoading={isLoading}
        />
      </div>

      <div className="mb-4 space-y-4">
        <fieldset className="mb-4 min-w-0 border-0 p-0">
          <legend className="sr-only">Generation mode</legend>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
            <div id="battle-mode-intro" className="min-w-0 flex-1">
              <p className="m-0 text-sm font-bold text-[var(--color-text)]">
                Battle mode
              </p>
              <p className="mt-1.5 mb-0 text-xs leading-relaxed text-[var(--color-text)] opacity-80">
                Generate the same quiz twice with Left Opponent and Right
                Opponent side by side in the quiz view, then pick the winner for
                your summary and refinements.
              </p>
            </div>
            <BattleModeSwitch
              checked={battleEnabled}
              labelledBy="battle-mode-intro"
              disabled={isLoading}
              onCheckedChange={(next) => {
                setBattleEnabled(next);
                if (next) setOpponentOverrideId(null);
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
        onExampleRowsChange={setExampleRows}
        isLoading={isLoading}
      />

      {localError ? (
        <p
          className="mb-3 text-sm text-[var(--color-destructive)]"
          role="alert"
        >
          {localError}
        </p>
      ) : null}

      <button
        type="submit"
        className="btn-primary w-full sm:w-auto"
        disabled={submitDisabled}
      >
        {isLoading ? "Generating…" : submitLabel}
      </button>
    </form>
  );
}
