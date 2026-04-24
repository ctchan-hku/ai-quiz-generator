import { Minus, Plus } from "lucide-react";
import { useState } from "react";
import {
  NUM_QUESTIONS_MAX,
  NUM_QUESTIONS_MIN,
  TOPIC_MAX_LENGTH,
  TOPIC_TEXTAREA_MIN_HEIGHT_PX,
} from "../config/quiz";
import type { ModelInfo } from "../types/api";
import type { QuizFormConfig } from "../types/quiz-machine";

interface QuizFormProps {
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
    onSubmit({ topic: trimmed, numQuestions, model });
  }

  function bump(delta: number) {
    const next = Math.min(
      NUM_QUESTIONS_MAX,
      Math.max(NUM_QUESTIONS_MIN, numQuestions + delta),
    );
    onNumQuestionsChange(next);
  }

  const modelFieldDisabled = isLoading || modelsLoading || models.length === 0;
  const submitDisabled =
    isLoading || modelsLoading || !!modelsError || models.length === 0;

  return (
    <form className="card text-left" onSubmit={handleSubmit}>
      <h2 className="mt-0 mb-4 font-[family-name:var(--font-heading)] text-xl font-semibold text-[var(--color-text)]">
        Topic
      </h2>
      <label
        className="mb-1 block text-sm font-bold text-[var(--color-text)]"
        htmlFor="quiz-topic"
      >
        What should the quiz cover?
      </label>
      <textarea
        id="quiz-topic"
        className="input mb-4 resize-y"
        style={{ minHeight: TOPIC_TEXTAREA_MIN_HEIGHT_PX }}
        placeholder="e.g. HKU history, organic chemistry, Python basics…"
        value={topic}
        onChange={(e) => onTopicChange(e.target.value)}
        disabled={isLoading}
        maxLength={TOPIC_MAX_LENGTH}
      />

      <div className="mb-4 flex flex-wrap items-end gap-6">
        <div>
          <span
            className="mb-1 block text-sm font-bold text-[var(--color-text)]"
            id="num-q-label"
          >
            Number of questions
          </span>
          <div
            className="flex items-center gap-2"
            role="group"
            aria-labelledby="num-q-label"
          >
            <button
              type="button"
              className="btn-secondary !p-2"
              onClick={() => bump(-1)}
              disabled={isLoading || numQuestions <= NUM_QUESTIONS_MIN}
              aria-label="Decrease question count"
            >
              <Minus className="h-5 w-5" aria-hidden />
            </button>
            <input
              type="text"
              readOnly
              className="input max-w-[4rem] text-center"
              value={numQuestions}
              aria-live="polite"
            />
            <button
              type="button"
              className="btn-secondary !p-2"
              onClick={() => bump(1)}
              disabled={isLoading || numQuestions >= NUM_QUESTIONS_MAX}
              aria-label="Increase question count"
            >
              <Plus className="h-5 w-5" aria-hidden />
            </button>
          </div>
          <p className="mt-1 mb-0 text-xs text-[var(--color-text)] opacity-75">
            Between {NUM_QUESTIONS_MIN} and {NUM_QUESTIONS_MAX}
          </p>
        </div>

        <div className="min-w-[12rem] flex-1">
          <label
            className="mb-1 block text-sm font-bold text-[var(--color-text)]"
            htmlFor="quiz-model"
          >
            Model
          </label>
          {modelsError ? (
            <p
              className="mb-0 text-sm text-[var(--color-destructive)]"
              role="alert"
            >
              Could not load models: {modelsError}
            </p>
          ) : (
            <select
              id="quiz-model"
              className="input cursor-pointer"
              value={model}
              onChange={(e) => onModelChange(e.target.value)}
              disabled={modelFieldDisabled}
            >
              {modelsLoading && models.length === 0 ? (
                <option value="">Loading models…</option>
              ) : models.length === 0 ? (
                <option value="">No models configured</option>
              ) : (
                models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))
              )}
            </select>
          )}
        </div>
      </div>

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
