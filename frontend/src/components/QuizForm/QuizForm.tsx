import { useState } from "react";
import {
  FEW_SHOT_MAX_COUNT,
  FEW_SHOT_MAX_LENGTH,
} from "../../config/quiz";
import type { QuizFormConfig } from "../../types/quiz-machine";
import { FewShotExamplesSection } from "./FewShotExamplesSection";
import { ModelField } from "./ModelField";
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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLocalError(null);
    const trimmed = topic.trim();
    if (!trimmed) {
      setLocalError("Please enter a topic before generating.");
      return;
    }
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

    const base: QuizFormConfig = {
      topic: trimmed,
      numQuestions,
      model,
    };
    if (fewShotNormalized.length > 0) {
      base.few_shot_examples = fewShotNormalized;
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

      <div className="mb-4 flex flex-wrap items-end gap-6">
        <NumberOfQuestionsField
          numQuestions={numQuestions}
          onNumQuestionsChange={onNumQuestionsChange}
          isLoading={isLoading}
        />
        <ModelField
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
