import type { Dispatch, SetStateAction } from "react";
import { useState } from "react";
import { ChevronRight } from "lucide-react";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import {
  USER_INSTRUCTION_MAX_LENGTH,
  USER_INSTRUCTIONS_MAX_COUNT,
} from "../../config/quiz-form";
import { QuizFormSectionTitle } from "./QuizFormSectionTitle";

interface UserInstructionsSectionProps {
  user_instructions: string[];
  onUserInstructionsChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

/** Each entry is one line (`<input type="text">`); server receives `user_instructions: string[]`. */
export function UserInstructionsSection({
  user_instructions,
  onUserInstructionsChange,
  isLoading,
}: UserInstructionsSectionProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <details
      className="mb-6 text-left"
      open={isOpen}
      onToggle={(e) => setIsOpen(e.currentTarget.open)}
    >
      <QuizFormSectionTitle
        as="summary"
        className="flex cursor-pointer list-none items-center gap-2 [&::-webkit-details-marker]:hidden"
      >
        <ChevronRight
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
            isOpen && "rotate-90",
          )}
          aria-hidden
        />
        Instructions
        <span className="sr-only">
          {isOpen ? "Collapse section" : "Expand section"}
        </span>
      </QuizFormSectionTitle>
      <div className="mt-3 space-y-3">
        {user_instructions.map((line, index) => (
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
                maxLength={USER_INSTRUCTION_MAX_LENGTH}
                autoComplete="off"
                placeholder="Optional tone, exclusions, grading emphasis…"
                value={line}
                onChange={(e) => {
                  const next = e.target.value;
                  onUserInstructionsChange((prev) => {
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
                onUserInstructionsChange((prev) =>
                  prev.filter((_, i) => i !== index),
                );
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
              if (user_instructions.length < USER_INSTRUCTIONS_MAX_COUNT) {
                onUserInstructionsChange((prev) => [...prev, ""]);
              }
            }}
            disabled={
              isLoading ||
              user_instructions.length >= USER_INSTRUCTIONS_MAX_COUNT
            }
          >
            Add line
          </Button>
          {user_instructions.length >= USER_INSTRUCTIONS_MAX_COUNT ? (
            <p className="mt-1.5 mb-0 text-xs text-muted-foreground">
              Maximum {USER_INSTRUCTIONS_MAX_COUNT} lines.
            </p>
          ) : null}
        </div>
      </div>
    </details>
  );
}
