import type { QuizResponse } from "../../types/quiz";
import { formatEstimatedCostUsd } from "../../lib/format-usd";

/** Single full-quiz metadata: model + cost in the review (hero) layout. */
export function QuizRunSummaryHero({ quiz }: { quiz: QuizResponse }) {
  return (
    <div className="card text-left">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-8">
        <div>
          <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
            Model
          </p>
          <p className="mt-0 mb-0 text-sm font-medium text-[var(--color-text)]">
            {quiz.model_used}
          </p>
        </div>
        <div>
          <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
            Cost (est.)
          </p>
          <p className="mt-0 mb-0 text-sm font-medium text-[var(--color-text)]">
            {formatEstimatedCostUsd(quiz.cost_usd)}
          </p>
        </div>
      </div>
      {quiz.truncated ? (
        <p className="mb-0 mt-3 text-xs text-[var(--color-text)] opacity-70">
          Source text was truncated
        </p>
      ) : null}
    </div>
  );
}
