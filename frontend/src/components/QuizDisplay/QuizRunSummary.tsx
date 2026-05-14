import type { ModelInfo, QuizResponse } from "../../api";
import { pipelineVersionCaption } from "../../config/quiz-form";
import { formatEstimatedCostUsd } from "../../lib/format-usd";
import { Card, CardContent } from "@/components/ui/card";

function modelDisplayLabel(models: ModelInfo[] | undefined, modelId: string) {
  return models?.find((m) => m.id === modelId)?.label ?? modelId;
}

/** Review header: model and estimated cost for the generated quiz. */
export function QuizRunSummaryHero({
  quiz,
  models,
  pipelineVersion,
}: {
  quiz: QuizResponse;
  models?: ModelInfo[];
  /** Same as generate-time `QuizFormConfig.pipeline_version` (v1 vs v2 quiz LLM pipelines). */
  pipelineVersion?: 1 | 2;
}) {
  return (
    <Card size="sm" className="text-left">
      <CardContent className="pt-0">
        <div
          className={`grid grid-cols-1 gap-4 sm:gap-8 ${pipelineVersion != null ? "sm:grid-cols-3" : "sm:grid-cols-2"}`}
        >
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
          {pipelineVersion != null ? (
            <div>
              <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Generation pipeline
              </p>
              <p className="mt-0 mb-0 text-sm font-medium text-foreground">
                {pipelineVersionCaption(pipelineVersion)}
              </p>
            </div>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
