import type { Dispatch, SetStateAction } from "react";
import { useState } from "react";
import { ChevronRight } from "lucide-react";

import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import {
  FEW_SHOT_MAX_COUNT,
  FEW_SHOT_MAX_LENGTH,
  FEW_SHOT_TEXTAREA_MIN_HEIGHT_PX,
  QUIZ_FORM_SECTION_TITLE_CLASS,
} from "../../config/quiz-form";

interface FewShotExamplesSectionProps {
  few_shot_examples: string[];
  onFewShotExamplesChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

export function FewShotExamplesSection({
  few_shot_examples,
  onFewShotExamplesChange,
  isLoading,
}: FewShotExamplesSectionProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <details
      className="mb-4 text-left"
      open={isOpen}
      onToggle={(e) => setIsOpen(e.currentTarget.open)}
    >
      <summary
        className={cn(
          "flex cursor-pointer list-none items-center gap-2 [&::-webkit-details-marker]:hidden",
          QUIZ_FORM_SECTION_TITLE_CLASS,
        )}
      >
        <ChevronRight
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
            isOpen && "rotate-90",
          )}
          aria-hidden
        />
        Examples
        <span className="sr-only">
          {isOpen ? "Collapse section" : "Expand section"}
        </span>
      </summary>
      <div className="mt-3 space-y-3">
        {few_shot_examples.map((row, index) => (
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
                  onFewShotExamplesChange((prev) => {
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
                onFewShotExamplesChange((prev) =>
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
              if (few_shot_examples.length < FEW_SHOT_MAX_COUNT) {
                onFewShotExamplesChange((prev) => [...prev, ""]);
              }
            }}
            disabled={
              isLoading || few_shot_examples.length >= FEW_SHOT_MAX_COUNT
            }
          >
            Add example
          </Button>
          {few_shot_examples.length >= FEW_SHOT_MAX_COUNT ? (
            <p className="mt-1.5 mb-0 text-xs text-muted-foreground">
              Maximum {FEW_SHOT_MAX_COUNT} examples.
            </p>
          ) : null}
        </div>
      </div>
    </details>
  );
}
