import type { ReactNode } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { cn } from "@/lib/cn";
import type { MultipleChoiceQuestion } from "@/api/contracts";
import { optionLabel } from "@/lib/mc-option-label";

export interface TestQuestionCardProps {
  questionIndex: number;
  question: MultipleChoiceQuestion;
  /** Shown at the top of the card (e.g. version selector). */
  header?: ReactNode;
  /** Shown below the explanation in a bordered footer (comments, edit). */
  footer?: ReactNode;
}

/** Shared MCQ shell: stem, options with correct highlighting, explanation. */
export function TestQuestionCard({
  questionIndex,
  question,
  header,
  footer,
}: TestQuestionCardProps) {
  const correctSet = new Set(question.correctIndices);
  const n = questionIndex + 1;

  return (
    <Card className="flex flex-col text-left shadow-md">
      {header != null ? (
        <CardHeader className="pb-3 pt-4">
          <div className="flex flex-wrap items-center gap-3">{header}</div>
        </CardHeader>
      ) : null}

      <CardContent className={cn("flex-grow", header == null && "pt-6")}>
        <h3 className="mt-0 mb-4 font-heading text-lg font-semibold text-foreground">
          <span className="text-primary">{n}.</span> {question.question}
        </h3>

        <ul
          className="m-0 flex list-none flex-col gap-3 p-0"
          aria-label="Answer choices (read-only)"
        >
          {question.options.map((opt, optIdx) => {
            const label = optionLabel(optIdx);
            const isCorrect = correctSet.has(optIdx);

            return (
              <li key={optIdx}>
                <div
                  className={cn(
                    "flex w-full items-start gap-3 rounded-lg border px-4 py-3 text-left transition-colors",
                    isCorrect
                      ? "border-primary/40 bg-primary/10 ring-1 ring-primary/40"
                      : "border-border bg-card/50",
                  )}
                >
                  <span
                    className={cn(
                      "font-bold",
                      isCorrect ? "text-primary" : "text-muted-foreground",
                    )}
                  >
                    {label}.
                  </span>
                  <span className="text-foreground">{opt}</span>
                </div>
              </li>
            );
          })}
        </ul>

        <div className="mt-6 rounded-lg bg-muted/50 p-4 text-sm leading-relaxed text-foreground">
          <span className="font-semibold block mb-1">Explanation</span>
          {question.explanation}
        </div>
      </CardContent>

      {footer != null ? (
        <CardFooter className="border-t border-border bg-muted/20 px-6 py-4">
          <div className="w-full">{footer}</div>
        </CardFooter>
      ) : null}
    </Card>
  );
}
