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
import type { ModelBoardRole } from "./modelBoardConfig";
import { MODEL_BOARD_CONFIG } from "./modelBoardConfig";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const MODELS_PER_PAGE = 5;

const priceGridClass =
  "grid w-full min-w-0 grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] gap-x-1.5 text-xs tabular-nums sm:gap-x-2 sm:text-sm";

const rowGridClass =
  "grid grid-cols-[minmax(0,1.6fr)_minmax(10rem,1.35fr)] items-center gap-x-3 gap-y-2 border-b border-border py-2.5 text-left sm:gap-x-4";

interface ModelBoardProps {
  model: string;
  onModelChange: (id: string | null) => void;
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  isLoading: boolean;
  /** Controls labels, radio grouping, and input ids (`standard` vs two battle slots). */
  boardRole?: ModelBoardRole;
}

export function ModelBoard({
  model,
  onModelChange,
  models,
  modelsLoading,
  modelsError,
  isLoading,
  boardRole = "standard",
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

  function inputDomId(modelId: string) {
    return `quiz-model-${boardRole}-${modelId}`;
  }

  function labelDomId(modelId: string) {
    return `model-row-label-${boardRole}-${modelId}`;
  }

  const roleUi = MODEL_BOARD_CONFIG[boardRole];

  const toggleSort = () => {
    setSortDirection((d) => (d === "price_asc" ? "price_desc" : "price_asc"));
    resetToFirstPage();
  };

  return (
    <div className="min-w-0 w-full">
      {modelsError ? (
        <p className="mb-0 text-sm text-destructive" role="alert">
          Could not load models: {modelsError}
        </p>
      ) : (
        <fieldset className="m-0 min-w-0 border-0 p-0">
          <legend className="sr-only">{roleUi.legendSr}</legend>
          <div className="mb-3 mt-0 flex flex-wrap items-center gap-2">
            <p className="mb-0 mt-0 text-sm font-bold text-foreground">
              {roleUi.titleBold}
            </p>
            <Badge
              variant="secondary"
              className="font-heading text-[10px] uppercase tracking-wide"
            >
              Poe API
            </Badge>
          </div>

          {modelsLoading && models.length === 0 ? (
            <p className="mb-0 text-sm text-muted-foreground">
              Loading models…
            </p>
          ) : models.length === 0 ? (
            <p className="mb-0 text-sm text-muted-foreground">
              No models configured
            </p>
          ) : (
            <>
              <div
                className={`${rowGridClass} bg-muted/50 px-2 font-heading text-xs font-semibold uppercase tracking-wide text-foreground sm:px-3`}
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
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-7 w-7"
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
                      <ArrowUp
                        className="h-4 w-4"
                        strokeWidth={2}
                        aria-hidden
                      />
                    ) : (
                      <ArrowDown
                        className="h-4 w-4"
                        strokeWidth={2}
                        aria-hidden
                      />
                    )}
                  </Button>
                </div>
              </div>

              <RadioGroup
                aria-label={roleUi.radioGroupAria}
                className="mb-3 rounded-lg border border-border bg-card px-2 sm:px-3 gap-0"
                value={model}
                onValueChange={onModelChange}
                disabled={modelFieldDisabled}
              >
                {pageItems.map((m) => {
                  const inputStr = formatUsdPerM(m.price?.input ?? null);
                  const outputStr = formatUsdPerM(m.price?.output ?? null);
                  const parts = priceCellParts(inputStr, outputStr);

                  const rowLabelId = labelDomId(m.id);

                  return (
                    <Label
                      key={m.id}
                      htmlFor={inputDomId(m.id)}
                      className={`${rowGridClass} cursor-pointer last:border-b-0 hover:bg-muted/50 font-normal`}
                    >
                      <div className="flex min-w-0 items-center gap-3">
                        <RadioGroupItem
                          id={inputDomId(m.id)}
                          value={m.id}
                          aria-labelledby={rowLabelId}
                        />
                        <span
                          id={rowLabelId}
                          className="min-w-0 truncate font-heading text-sm font-semibold text-foreground"
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
                          className={`items-center text-foreground ${priceGridClass}`}
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
                    </Label>
                  );
                })}
              </RadioGroup>

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
