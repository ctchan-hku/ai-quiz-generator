import { useMemo, useState } from "react";

import type { ModelInfo } from "../../types/api";

type ModelSortDirection = "price_asc" | "price_desc";

function priceSortKey(m: ModelInfo): number {
  const normalizedInput = m.price?.input ?? Number.POSITIVE_INFINITY;
  const normalizedOutput = m.price?.output ?? Number.POSITIVE_INFINITY;
  return normalizedInput + normalizedOutput;
}

function sortedModels(
  models: ModelInfo[],
  direction: ModelSortDirection,
): ModelInfo[] {
  const copy = [...models];
  copy.sort((a, b) => {
    let cmp = priceSortKey(a) - priceSortKey(b);
    if (direction === "price_desc") {
      cmp = -cmp;
    }
    if (cmp !== 0) {
      return cmp;
    }
    const byLabel = a.label.localeCompare(b.label);
    if (byLabel !== 0) {
      return byLabel;
    }
    return a.id.localeCompare(b.id);
  });
  return copy;
}

const usdPerM = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

function formatUsdPerM(value: number | null): string | null {
  if (value == null) {
    return null;
  }
  return `${usdPerM.format(value)}/M`;
}

interface ModelBoardProps {
  model: string;
  onModelChange: (id: string | null) => void;
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  isLoading: boolean;
}

export function ModelBoard({
  model,
  onModelChange,
  models,
  modelsLoading,
  modelsError,
  isLoading,
}: ModelBoardProps) {
  const [sortDirection, setSortDirection] =
    useState<ModelSortDirection>("price_asc");

  const orderedModels = useMemo(
    () => sortedModels(models, sortDirection),
    [models, sortDirection],
  );

  const modelFieldDisabled = isLoading || modelsLoading || models.length === 0;

  return (
    <div className="min-w-0 flex-1">
      {modelsError ? (
        <p
          className="mb-0 text-sm text-[var(--color-destructive)]"
          role="alert"
        >
          Could not load models: {modelsError}
        </p>
      ) : (
        <fieldset className="m-0 min-w-0 border-0 p-0">
          <legend className="mb-1 block text-sm font-bold text-[var(--color-text)]">
            Model
          </legend>

          <div className="mb-3 flex flex-wrap gap-2">
            <button
              type="button"
              className="btn-secondary px-3 py-1.5 text-xs"
              aria-pressed={sortDirection === "price_asc"}
              disabled={modelFieldDisabled}
              onClick={() => setSortDirection("price_asc")}
            >
              Price: Low to high
            </button>
            <button
              type="button"
              className="btn-secondary px-3 py-1.5 text-xs"
              aria-pressed={sortDirection === "price_desc"}
              disabled={modelFieldDisabled}
              onClick={() => setSortDirection("price_desc")}
            >
              Price: High to low
            </button>
          </div>

          {modelsLoading && models.length === 0 ? (
            <p className="mb-0 text-sm text-[var(--color-text)] opacity-80">
              Loading models…
            </p>
          ) : models.length === 0 ? (
            <p className="mb-0 text-sm text-[var(--color-text)] opacity-80">
              No models configured
            </p>
          ) : (
            <div
              role="radiogroup"
              aria-label="Model choice"
              className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3"
            >
              {orderedModels.map((m) => {
                const inputStr = formatUsdPerM(m.price?.input ?? null);
                const outputStr = formatUsdPerM(m.price?.output ?? null);
                const pricingUnavailable =
                  m.price == null ||
                  (m.price.input == null && m.price.output == null);

                const labelId = `model-card-label-${m.id}`;

                return (
                  <label
                    key={m.id}
                    htmlFor={`quiz-model-${m.id}`}
                    className={
                      "flex cursor-pointer flex-col gap-2 rounded-lg border px-3 py-3 text-left transition-colors " +
                      (model === m.id
                        ? "border-[var(--color-primary)]/50 bg-[var(--color-primary)]/10 ring-2 ring-[var(--color-primary)]/35"
                        : "border-[rgb(30_41_59/0.12)] bg-white/30 hover:border-[rgb(30_41_59/0.2)]")
                    }
                  >
                    <div className="flex items-start gap-2">
                      <input
                        id={`quiz-model-${m.id}`}
                        type="radio"
                        name="quiz-model-choice"
                        value={m.id}
                        checked={model === m.id}
                        disabled={modelFieldDisabled}
                        onChange={() => onModelChange(m.id)}
                        className="mt-1"
                        aria-labelledby={labelId}
                      />
                      <div className="min-w-0 flex-1">
                        <div
                          id={labelId}
                          className="font-[family-name:var(--font-heading)] text-sm font-semibold text-[var(--color-text)]"
                        >
                          {m.label}
                        </div>
                        <div className="mt-0.5 break-all font-mono text-xs text-[var(--color-text)] opacity-75">
                          {m.id}
                        </div>
                        {pricingUnavailable ? (
                          <p className="mb-0 mt-2 text-xs text-[var(--color-text)] opacity-80">
                            Pricing unavailable
                          </p>
                        ) : (
                          <ul className="m-0 mt-2 list-none space-y-1 p-0 text-xs text-[var(--color-text)]">
                            {inputStr ? (
                              <li>{inputStr} input</li>
                            ) : (
                              <li className="opacity-70">Input: —</li>
                            )}
                            {outputStr ? (
                              <li>{outputStr} output</li>
                            ) : (
                              <li className="opacity-70">Output: —</li>
                            )}
                          </ul>
                        )}
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          )}
        </fieldset>
      )}
    </div>
  );
}
