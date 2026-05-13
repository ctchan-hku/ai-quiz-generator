import type { ModelInfo } from "../../types/api";
import type { QuizFormConfig } from "../../types/quiz-machine";
import type { QuizResponse } from "../../types/quiz";
import { formatEstimatedCostUsd } from "../../lib/format-usd";
import { toQuizGenerationRequestSnapshot } from "../../lib/export-quiz/journal";
import { GenerationSettingsSummary } from "../GenerationSettingsSummary";
import { Card, CardContent } from "@/components/ui/card";

/** Review header: user’s form inputs (when provided) plus model / cost for the generated quiz. */
export function QuizRunSummaryHero({
  quiz,
  topic,
  generationForm,
  models,
}: {
  quiz: QuizResponse;
  topic?: string;
  generationForm?: QuizFormConfig;
  models?: ModelInfo[];
}) {
  const snapshot =
    generationForm != null
      ? toQuizGenerationRequestSnapshot(generationForm)
      : null;
  const topicDisplay = (topic ?? generationForm?.topic ?? "").trim();

  return (
    <Card className="text-left">
      <CardContent className="pt-6">
        <GenerationSettingsSummary
          topic={topicDisplay}
          snapshot={snapshot}
          models={models}
        />
        {snapshot != null ? (
          <p className="mb-3 mt-0 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Quiz output
          </p>
        ) : null}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-8">
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Model
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {quiz.model_used}
            </p>
          </div>
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Cost (est.)
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {formatEstimatedCostUsd(quiz.cost_usd)}
            </p>
          </div>
        </div>
        {quiz.truncated ? (
          <p className="mb-0 mt-3 text-xs text-muted-foreground">
            Source text was truncated
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}
