import type { Dispatch, SetStateAction } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  USER_INSTRUCTION_LINE_MAX_CHARS,
  USER_INSTRUCTIONS_MAX,
} from "../../config/quiz";

interface UserInstructionsLinesSectionProps {
  lines: string[];
  onLinesChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

/** Each entry is one line (`<input type="text">`); server receives `user_instructions: string[]`. */
export function UserInstructionsLinesSection({
  lines,
  onLinesChange,
  isLoading,
}: UserInstructionsLinesSectionProps) {
  return (
    <details className="mb-6 text-left">
      <summary className="cursor-pointer font-heading text-sm font-semibold text-foreground">
        Quiz-specific instructions{" "}
        <span className="font-normal text-muted-foreground">
          (optional; merged with field rules, not examples)
        </span>
      </summary>
      <div className="mt-3 space-y-3 pl-0">
        {lines.map((line, index) => (
          <div
            key={index}
            className="flex flex-col gap-2 sm:flex-row sm:items-end"
          >
            <div className="min-w-0 flex-1">
              <Label
                className="mb-2 block text-xs font-bold text-foreground"
                htmlFor={`quiz-user-instruction-${index}`}
              >
                Line {index + 1}
              </Label>
              <Input
                id={`quiz-user-instruction-${index}`}
                type="text"
                className="w-full max-w-full min-w-0"
                maxLength={USER_INSTRUCTION_LINE_MAX_CHARS}
                autoComplete="off"
                placeholder="Optional tone, exclusions, grading emphasis…"
                value={line}
                onChange={(e) => {
                  const next = e.target.value;
                  onLinesChange((prev) => {
                    const copy = [...prev];
                    copy[index] = next;
                    return copy;
                  });
                }}
                disabled={isLoading}
              />
            </div>
            <Button
              type="button"
              variant="secondary"
              className="shrink-0"
              onClick={() => {
                onLinesChange((prev) => prev.filter((_, i) => i !== index));
              }}
              disabled={isLoading}
              aria-label={`Remove instruction line ${index + 1}`}
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
              if (lines.length < USER_INSTRUCTIONS_MAX) {
                onLinesChange((prev) => [...prev, ""]);
              }
            }}
            disabled={isLoading || lines.length >= USER_INSTRUCTIONS_MAX}
          >
            Add line
          </Button>
          {lines.length >= USER_INSTRUCTIONS_MAX ? (
            <p className="mt-1.5 mb-0 text-xs text-muted-foreground">
              Maximum {USER_INSTRUCTIONS_MAX} lines.
            </p>
          ) : null}
        </div>
      </div>
    </details>
  );
}
