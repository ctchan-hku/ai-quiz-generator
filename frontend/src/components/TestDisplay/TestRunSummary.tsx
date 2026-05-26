import type { ModelInfo, GenerateTestResponse } from "../../api";
import { pipelineVersionCaption } from "../../config/test-form";
import { formatEstimatedCostUsd } from "../../lib/format-usd";
import { Card, CardContent } from "@/components/ui/card";

function modelDisplayLabel(models: ModelInfo[] | undefined, modelId: string) {
  return models?.find((m) => m.id === modelId)?.label ?? modelId;
}

/** Review header: model and estimated cost for the generated test. */
export function TestRunSummaryHero({
  test,
  models,
  pipelineVersion,
}: {
  test: GenerateTestResponse;
  models?: ModelInfo[];
  /** Same as generate-time `TestFormConfig.pipeline_version` (v1 vs v2 test LLM pipelines). */
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
              {modelDisplayLabel(models, test.model_used)}
            </p>
          </div>
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Cost (est.)
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {formatEstimatedCostUsd(test.cost_usd)}
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
