import type { ReactNode } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import type { MultipleChoiceQuestion } from "@/api/contracts";

export interface TestQuestionCardProps {
  questionIndex: number;
  question: MultipleChoiceQuestion;
  /** Parallel to `question.options` (e.g. A, B, C). */
  optionLabels: string[];
  /** Shown at the top of the card (e.g. version selector). */
  header?: ReactNode;
  /** Shown below the explanation in a bordered footer (comments, edit). */
  footer?: ReactNode;
}

/** Shared MCQ shell: stem, options with correct highlighting, explanation. */
export function TestQuestionCard({
  questionIndex,
  question,
  optionLabels,
  header,
  footer,
}: TestQuestionCardProps) {
  const correctSet = new Set(question.correctIndices);
  const n = questionIndex + 1;
  const contentClass = header == null ? "flex-grow pt-6" : "flex-grow";

  return (
    <Card className="flex flex-col text-left shadow-md">
      {header != null ? (
        <CardHeader className="pb-3 pt-4">
          <div className="flex flex-wrap items-center gap-3">{header}</div>
        </CardHeader>
      ) : null}

      <CardContent className={contentClass}>
        <h3 className="mt-0 mb-4 font-heading text-lg font-semibold text-foreground">
          <span className="text-primary">{n}.</span> {question.question}
        </h3>

        <ul
          className="m-0 flex list-none flex-col gap-3 p-0"
          aria-label="Answer choices (read-only)"
        >
          {question.options.map((opt, optIdx) => {
            const label = optionLabels[optIdx] ?? String(optIdx + 1);
            const isCorrect = correctSet.has(optIdx);
            return (
              <li
                key={optIdx}
                className={`rounded-md border px-4 py-3 text-sm ${
                  isCorrect
                    ? "border-primary/40 bg-primary/5 font-medium text-foreground"
                    : "border-border bg-muted/30 text-foreground"
                }`}
              >
                <span className="font-semibold text-primary">{label}.</span>{" "}
                {opt}
              </li>
            );
          })}
        </ul>

        {question.explanation.trim() !== "" ? (
          <div className="mt-6 rounded-md border border-border bg-muted/20 px-4 py-3">
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Explanation
            </p>
            <p className="mt-0 mb-0 text-sm text-foreground">
              {question.explanation}
            </p>
          </div>
        ) : null}
      </CardContent>

      {footer != null ? (
        <CardFooter className="flex flex-col items-stretch border-t border-border pt-4">
          {footer}
        </CardFooter>
      ) : null}
    </Card>
  );
}
