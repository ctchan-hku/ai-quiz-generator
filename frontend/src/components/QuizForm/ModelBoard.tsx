import { useMemo, useState } from "react";

import { ArrowDown, ArrowUp } from "lucide-react";

import type { ModelInfo } from "../../types/api";
import { PageNav } from "../common/PageNav";
import { usePagination } from "../../hooks/usePagination";
import {
  formatUsdPerM,
  priceCellParts,
  sortedModels,
  type ModelSortDirection,
} from "../../lib/modelBoard";

const MODELS_PER_PAGE = 5;

const priceGridClass =
  "grid w-full min-w-0 grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] gap-x-1.5 text-xs tabular-nums sm:gap-x-2 sm:text-sm";

const rowGridClass =
  "grid grid-cols-[minmax(0,1.6fr)_minmax(10rem,1.35fr)] items-center gap-x-3 gap-y-2 border-b border-[rgb(30_41_59/0.1)] py-2.5 text-left sm:gap-x-4";

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
          <div className="mb-3 mt-0 flex flex-wrap items-center gap-2">
            <p className="mb-0 mt-0 text-sm font-bold text-[var(--color-text)]">
              Model leaderboard
            </p>
            <span className="inline-flex shrink-0 rounded-full border border-[rgb(30_41_59/0.2)] bg-[rgb(30_41_59/0.06)] px-2.5 py-0.5 font-[family-name:var(--font-heading)] text-[10px] font-semibold uppercase tracking-wide text-[var(--color-text)]">
              Poe API
            </span>
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
            <>
              <div
                className={`${rowGridClass} bg-[rgb(30_41_59/0.04)] px-2 font-[family-name:var(--font-heading)] text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] sm:px-3`}
              >
                <span>Model</span>
                <div className="flex min-w-0 items-center justify-end gap-2 sm:justify-start">
                  <div
                    className={`min-w-0 flex-1 items-start ${priceGridClass}`}
                  >
                    <span className="whitespace-nowrap text-right">Input</span>
                    <span className="select-none whitespace-nowrap px-0.5 text-center">
                      /
                    </span>
                    <span className="min-w-0 text-center leading-snug sm:text-left">
                      <span className="whitespace-nowrap">Output</span>{" "}
                      <span className="whitespace-nowrap">(USD/M)</span>
                    </span>
                  </div>
                  <button
                    type="button"
                    className="flex size-7 shrink-0 items-center justify-center rounded-md border border-[rgb(30_41_59/0.15)] bg-white/60 text-[var(--color-text)] transition-colors hover:bg-[rgb(30_41_59/0.08)] disabled:pointer-events-none disabled:opacity-50"
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
                      <ArrowUp className="size-4" strokeWidth={2} aria-hidden />
                    ) : (
                      <ArrowDown
                        className="size-4"
                        strokeWidth={2}
                        aria-hidden
                      />
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
                  const parts = priceCellParts(inputStr, outputStr);

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
                      <div
                        className="flex min-w-0 justify-end sm:justify-start"
                        role="group"
                        aria-label={parts.label}
                      >
                        <div
                          className={`items-center text-[var(--color-text)] ${priceGridClass}`}
                        >
                          <span className="min-w-0 text-right">
                            {parts.input}
                          </span>
                          <span
                            className="select-none px-0.5 text-center"
                            aria-hidden
                          >
                            /
                          </span>
                          <span className="min-w-0 text-left">
                            {parts.output}
                          </span>
                        </div>
                      </div>
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
