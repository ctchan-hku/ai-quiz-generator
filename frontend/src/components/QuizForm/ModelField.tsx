import type { ModelInfo } from "../../types/api";

interface ModelFieldProps {
  model: string;
  onModelChange: (id: string | null) => void;
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  isLoading: boolean;
}

export function ModelField({
  model,
  onModelChange,
  models,
  modelsLoading,
  modelsError,
  isLoading,
}: ModelFieldProps) {
  const modelFieldDisabled = isLoading || modelsLoading || models.length === 0;

  return (
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
  );
}
