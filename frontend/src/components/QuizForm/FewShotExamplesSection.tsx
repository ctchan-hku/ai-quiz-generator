import type { Dispatch, SetStateAction } from "react";
import {
  FEW_SHOT_MAX_COUNT,
  FEW_SHOT_MAX_LENGTH,
  FEW_SHOT_TEXTAREA_MIN_HEIGHT_PX,
} from "../../config/quiz";

interface FewShotExamplesSectionProps {
  exampleRows: string[];
  onExampleRowsChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

export function FewShotExamplesSection({
  exampleRows,
  onExampleRowsChange,
  isLoading,
}: FewShotExamplesSectionProps) {
  return (
    <details className="mb-4 text-left">
      <summary className="cursor-pointer font-[family-name:var(--font-heading)] text-sm font-semibold text-[var(--color-text)]">
        Example / style hints
      </summary>
      <div className="mt-3 space-y-3 pl-0">
        {exampleRows.map((row, index) => (
          <div
            key={index}
            className="flex flex-col gap-2 sm:flex-row sm:items-end"
          >
            <div className="min-w-0 flex-1">
              <label
                className="mb-1 block text-xs font-bold text-[var(--color-text)]"
                htmlFor={`quiz-few-shot-${index}`}
              >
                Example {index + 1}
              </label>
              <textarea
                id={`quiz-few-shot-${index}`}
                className="input resize-y"
                style={{ minHeight: FEW_SHOT_TEXTAREA_MIN_HEIGHT_PX }}
                value={row}
                onChange={(e) => {
                  const next = e.target.value;
                  onExampleRowsChange((prev) => {
                    const copy = [...prev];
                    copy[index] = next;
                    return copy;
                  });
                }}
                disabled={isLoading}
                maxLength={FEW_SHOT_MAX_LENGTH}
                placeholder="Optional sample question tone or format to match…"
              />
            </div>
            <button
              type="button"
              className="btn-secondary shrink-0"
              onClick={() => {
                onExampleRowsChange((prev) =>
                  prev.filter((_, i) => i !== index),
                );
              }}
              disabled={isLoading}
              aria-label={`Remove example ${index + 1}`}
            >
              Remove
            </button>
          </div>
        ))}
        <div>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              if (exampleRows.length < FEW_SHOT_MAX_COUNT) {
                onExampleRowsChange((prev) => [...prev, ""]);
              }
            }}
            disabled={isLoading || exampleRows.length >= FEW_SHOT_MAX_COUNT}
          >
            Add example
          </button>
          {exampleRows.length >= FEW_SHOT_MAX_COUNT ? (
            <p className="mt-1 mb-0 text-xs text-[var(--color-text)] opacity-75">
              Maximum {FEW_SHOT_MAX_COUNT} examples.
            </p>
          ) : null}
        </div>
      </div>
    </details>
  );
}
