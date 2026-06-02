import { ArrowDown, ArrowUp } from "lucide-react";
import type { ModelInfo } from "@/api/contracts";
import { PageNav } from "@/components/common/PageNav";
import { useModelBoard, type ModelBoardRole } from "@/hooks/useModelBoard";
import { TestFormSectionTitle } from "./TestFormSectionTitle";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const rowGridClass =
  "grid grid-cols-[minmax(0,1.6fr)_minmax(10rem,1.35fr)] items-center gap-x-3 gap-y-2 border-b border-border py-2.5 text-left sm:gap-x-4";

interface ModelBoardProps {
  model: string;
  onModelChange: (id: string | null) => void;
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  isLoading: boolean;
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
  const {
    costColumn,
    setCostColumn,
    sortDirection,
    toggleSort,
    pageItems,
    nav,
    roleUi,
    pipelineSelectId,
    costLabelForModelId,
    inputDomId,
    labelDomId,
  } = useModelBoard({ model, models, boardRole });

  const modelFieldDisabled = isLoading || modelsLoading || models.length === 0;

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
            <TestFormSectionTitle as="p" className="mb-0 mt-0">
              {roleUi.titleBold}
            </TestFormSectionTitle>
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
                <div className="flex min-w-0 flex-col gap-2 normal-case tracking-normal">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 pt-0.5 text-left">
                      <span className="block text-[10px] font-medium leading-none text-muted-foreground">
                        Cost
                      </span>
                      <span className="mt-0.5 block text-xs font-semibold leading-snug text-foreground">
                        USD per question
                      </span>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      className="h-7 w-7 shrink-0"
                      disabled={modelFieldDisabled}
                      aria-pressed={sortDirection === "desc"}
                      aria-label={
                        sortDirection === "asc"
                          ? "USD per question sorted low to high; switch to high to low"
                          : "USD per question sorted high to low; switch to low to high"
                      }
                      onClick={toggleSort}
                    >
                      {sortDirection === "asc" ? (
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
                  <div className="flex flex-col gap-1">
                    <Label
                      htmlFor={pipelineSelectId}
                      className="text-[10px] font-medium text-muted-foreground"
                    >
                      Generation pipeline
                    </Label>
                    <Select
                      value={costColumn}
                      onValueChange={(v) =>
                        setCostColumn(v === "v1" ? "v1" : "v2")
                      }
                      disabled={modelFieldDisabled}
                    >
                      <SelectTrigger
                        id={pipelineSelectId}
                        size="sm"
                        className="h-8 w-full"
                      >
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="v1">Version 1</SelectItem>
                        <SelectItem value="v2">Version 2</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
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
                      <div className="min-w-0 text-right tabular-nums text-sm text-foreground">
                        {costLabelForModelId(m.id)}
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
