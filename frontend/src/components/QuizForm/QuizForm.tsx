import { useState } from "react";
import {
  FEW_SHOT_MAX_COUNT,
  FEW_SHOT_MAX_LENGTH,
  USER_INSTRUCTION_LINE_MAX_CHARS,
  USER_INSTRUCTIONS_MAX,
} from "../../config/quiz";
import type { QuizFormConfig } from "../../types/quiz-machine";
import { FewShotExamplesSection } from "./FewShotExamplesSection";
import { UserInstructionsLinesSection } from "./UserInstructionsLinesSection";
import { ModelBoard } from "./ModelBoard";
import { NumberOfQuestionsField } from "./NumberOfQuestionsField";
import { TopicField } from "./TopicField";
import type { QuizFormProps } from "./types";

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

      <div className="mb-4">
        <ModelBoard
          model={model}
          onModelChange={onModelChange}
          models={models}
          modelsLoading={modelsLoading}
          modelsError={modelsError}
          isLoading={isLoading}
        />
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
        {isLoading ? "Generating…" : "Generate Quiz"}
      </button>
    </form>
  );
}
