import type { ModelInfo } from "../../types/api";
import type { QuizResponse } from "../../types/quiz";
import { formatEstimatedCostUsd } from "../../lib/format-usd";
import { Card, CardContent } from "@/components/ui/card";

function modelDisplayLabel(models: ModelInfo[] | undefined, modelId: string) {
  return models?.find((m) => m.id === modelId)?.label ?? modelId;
}

/** Review header: model and estimated cost for the generated quiz. */
export function QuizRunSummaryHero({
  quiz,
  models,
}: {
  quiz: QuizResponse;
  models?: ModelInfo[];
}) {
  return (
    <Card size="sm" className="text-left">
      <CardContent className="pt-0">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-8">
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Model
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {modelDisplayLabel(models, quiz.model_used)}
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
