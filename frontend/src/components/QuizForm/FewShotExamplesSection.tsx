import type { Dispatch, SetStateAction } from "react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
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
      <summary className="cursor-pointer font-heading text-sm font-semibold text-foreground">
        Example / style hints
      </summary>
      <div className="mt-3 space-y-3 pl-0">
        {exampleRows.map((row, index) => (
          <div
            key={index}
            className="flex flex-col gap-2 sm:flex-row sm:items-end"
          >
            <div className="min-w-0 flex-1">
              <Label
                className="mb-2 block text-xs font-bold text-foreground"
                htmlFor={`quiz-few-shot-${index}`}
              >
                Example {index + 1}
              </Label>
              <Textarea
                id={`quiz-few-shot-${index}`}
                className="resize-y"
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
            <Button
              type="button"
              variant="secondary"
              className="shrink-0"
              onClick={() => {
                onExampleRowsChange((prev) =>
                  prev.filter((_, i) => i !== index),
                );
              }}
              disabled={isLoading}
              aria-label={`Remove example ${index + 1}`}
            >
              Remove
            </Button>
          </div>
        ))}
        <div>
          <Button
            type="button"
            variant="secondary"
            onClick={() => {
              if (exampleRows.length < FEW_SHOT_MAX_COUNT) {
                onExampleRowsChange((prev) => [...prev, ""]);
              }
            }}
            disabled={isLoading || exampleRows.length >= FEW_SHOT_MAX_COUNT}
          >
            Add example
          </Button>
          {exampleRows.length >= FEW_SHOT_MAX_COUNT ? (
            <p className="mt-1.5 mb-0 text-xs text-muted-foreground">
              Maximum {FEW_SHOT_MAX_COUNT} examples.
            </p>
          ) : null}
        </div>
      </div>
    </details>
  );
}
