import type { ReactNode } from "react";

import type { MultipleChoiceQuestion } from "../../types/quiz";
import { optionLabel } from "../../lib/option";

export interface QuizQuestionCardProps {
  questionIndex: number;
  question: MultipleChoiceQuestion;
  /** Shown at the top of the card (e.g. version selector). */
  header?: ReactNode;
  /** Shown below the explanation in a bordered footer (comments, refine). */
  footer?: ReactNode;
}

/** Shared MCQ shell: stem, options with correct highlighting, explanation. */
export function QuizQuestionCard({
  questionIndex,
  question,
  header,
  footer,
}: QuizQuestionCardProps) {
  const correctSet = new Set(question.correct_indices);
  const n = questionIndex + 1;

  return (
    <article className="card flex flex-col text-left shadow-[var(--shadow-lg)]">
      {header != null ? (
        <div className="mb-3 flex flex-wrap items-center gap-3">{header}</div>
      ) : null}

      <div className="flex-grow">
        <h3 className="mt-0 mb-2 font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-text)]">
          <span className="text-[var(--color-primary)]">{n}.</span>{" "}
          {question.question}
        </h3>

        <ul
          className="m-0 flex list-none flex-col gap-2 p-0"
          aria-label="Answer choices (read-only)"
        >
          {question.options.map((opt, optIdx) => {
            const label = optionLabel(optIdx);
            const isCorrect = correctSet.has(optIdx);
            let optionClass =
              "flex w-full items-start gap-3 rounded-lg border px-3 py-3 text-left";
            optionClass += isCorrect
              ? " border-[var(--color-primary)]/30 bg-[var(--color-primary)]/10 ring-2 ring-[var(--color-primary)]/40"
              : " border-[rgb(30_41_59/0.08)] bg-white/35 opacity-[0.72]";

            return (
              <li key={optIdx}>
                <div className={optionClass}>
                  <span className="font-bold text-[var(--color-primary)]">
                    {label}.
                  </span>
                  <span className="text-[var(--color-text)]">{opt}</span>
                </div>
              </li>
            );
          })}
        </ul>

        <p className="mb-0 mt-4 text-sm leading-relaxed text-[var(--color-text)]">
          <span className="font-semibold text-[var(--color-text)]">
            Explanation:{" "}
          </span>
          {question.explanation}
        </p>
      </div>

      {footer != null ? (
        <div className="border-t border-[rgb(30_41_59/0.1)] pt-4">{footer}</div>
      ) : null}
    </article>
  );
}
