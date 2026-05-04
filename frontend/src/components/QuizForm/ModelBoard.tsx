import { useMemo, useState } from "react";

import type { ModelInfo } from "../../types/api";
import { PageNav } from "../common/PageNav";
import { usePagination } from "../../hooks/usePagination";
import {
  formatUsdPerM,
  isPricingUnavailable,
  sortedModels,
  type ModelSortDirection,
} from "../../lib/modelBoard";

const MODELS_PER_PAGE = 5;

/** Leaderboard row / header grid: model | input $/M | output $/M | sort (header only). */
const rowGridClass =
  "grid grid-cols-[minmax(0,1.6fr)_minmax(5rem,1fr)_minmax(5rem,1fr)_auto] items-center gap-x-3 gap-y-2 border-b border-[rgb(30_41_59/0.1)] py-2.5 text-left sm:gap-x-4";

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

  const { pageItems, nav, resetToFirstPage } = usePagination(
    orderedModels,
    MODELS_PER_PAGE,
  );

  const modelFieldDisabled = isLoading || modelsLoading || models.length === 0;

  const toggleSort = () => {
    setSortDirection((d) => (d === "price_asc" ? "price_desc" : "price_asc"));
    resetToFirstPage();
  };

  return (
    <div className="min-w-0 w-full">
      {modelsError ? (
        <p
          className="mb-0 text-sm text-[var(--color-destructive)]"
          role="alert"
        >
          Could not load models: {modelsError}
        </p>
      ) : (
        <fieldset className="m-0 min-w-0 border-0 p-0">
          <legend className="sr-only">Choose a model</legend>
          <p className="mb-3 mt-0 text-sm font-bold text-[var(--color-text)]">
            Model leaderboard
          </p>

          {modelsLoading && models.length === 0 ? (
            <p className="mb-0 text-sm text-[var(--color-text)] opacity-80">
              Loading models…
            </p>
          ) : models.length === 0 ? (
            <p className="mb-0 text-sm text-[var(--color-text)] opacity-80">
              No models configured
            </p>
          ) : (
            <>
              <div
                className={`${rowGridClass} bg-[rgb(30_41_59/0.04)] px-2 font-[family-name:var(--font-heading)] text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] sm:px-3`}
              >
                <span>Model</span>
                <span className="text-right sm:text-left">Input ($/M USD)</span>
                <span className="text-right sm:text-left">Output ($/M USD)</span>
                <div className="flex justify-end">
                  <button
                    type="button"
                    className="btn-secondary shrink-0 px-2 py-1 text-xs font-normal normal-case tracking-normal"
                    disabled={modelFieldDisabled}
                    aria-pressed={sortDirection === "price_desc"}
                    aria-label={
                      sortDirection === "price_asc"
                        ? "Prices sorted low to high (models without pricing listed last); switch to high to low"
                        : "Prices sorted high to low (models without pricing listed last); switch to low to high"
                    }
                    onClick={toggleSort}
                  >
                    {sortDirection === "price_asc" ? (
                      <>Order ↑ Low to high</>
                    ) : (
                      <>Order ↓ High to low</>
                    )}
                  </button>
                </div>
              </div>

              <div
                role="radiogroup"
                aria-label="Model choice"
                className="mb-3 rounded-lg border border-[rgb(30_41_59/0.08)] bg-white/20 px-2 sm:px-3"
              >
                {pageItems.map((m) => {
                  const inputStr = formatUsdPerM(m.price?.input ?? null);
                  const outputStr = formatUsdPerM(m.price?.output ?? null);
                  const pricingUnavailable = isPricingUnavailable(m);

                  const labelId = `model-row-label-${m.id}`;

                  return (
                    <label
                      key={m.id}
                      htmlFor={`quiz-model-${m.id}`}
                      className={`${rowGridClass} cursor-pointer last:border-b-0 hover:bg-[rgb(30_41_59/0.03)]`}
                    >
                      <div className="flex min-w-0 items-center gap-2">
                        <input
                          id={`quiz-model-${m.id}`}
                          type="radio"
                          name="quiz-model-choice"
                          value={m.id}
                          checked={model === m.id}
                          disabled={modelFieldDisabled}
                          onChange={() => onModelChange(m.id)}
                          className="shrink-0"
                          aria-labelledby={labelId}
                        />
                        <span
                          id={labelId}
                          className="min-w-0 truncate font-[family-name:var(--font-heading)] text-sm font-semibold text-[var(--color-text)]"
                        >
                          {m.label}
                        </span>
                      </div>
                      <div className="text-xs text-[var(--color-text)] sm:text-sm">
                        {pricingUnavailable ? (
                          <span className="opacity-70">—</span>
                        ) : inputStr ? (
                          inputStr.replace(/\/M$/, "")
                        ) : (
                          <span className="opacity-70">—</span>
                        )}
                      </div>
                      <div className="text-xs text-[var(--color-text)] sm:text-sm">
                        {pricingUnavailable ? (
                          <span className="opacity-70">—</span>
                        ) : outputStr ? (
                          outputStr.replace(/\/M$/, "")
                        ) : (
                          <span className="opacity-70">—</span>
                        )}
                      </div>
                      <span className="min-w-[7rem]" aria-hidden="true" />
                    </label>
                  );
                })}
              </div>

              <PageNav
                pagination={nav}
                disabled={modelFieldDisabled}
                navAriaLabel="Model list pages"
              />
            </>
          )}
        </fieldset>
      )}
    </div>
  );
}
