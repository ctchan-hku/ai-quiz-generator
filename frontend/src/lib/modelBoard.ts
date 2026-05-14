import type { ModelInfo } from "../api";
import { modelGenerationCostPerQuestionUsd } from "../config/model-generation-cost";

export type CostPipelineColumn = "v1" | "v2";
export type CostSortDirection = "asc" | "desc";

function costPerQuestion(modelId: string, version: CostPipelineColumn): number {
  const row =
    modelGenerationCostPerQuestionUsd[
      modelId as keyof typeof modelGenerationCostPerQuestionUsd
    ];
  if (!row) {
    return 0;
  }
  return row[version];
}

export function costPerQuestionForPipeline(
  modelId: string,
  version: CostPipelineColumn,
): number {
  return costPerQuestion(modelId, version);
}

export function sortedModelsByCostColumn(
  models: ModelInfo[],
  direction: CostSortDirection,
  version: CostPipelineColumn,
): ModelInfo[] {
  return [...models].sort((a, b) => {
    let cmp = costPerQuestion(a.id, version) - costPerQuestion(b.id, version);
    if (direction === "desc") {
      cmp = -cmp;
    }
    if (cmp !== 0) {
      return cmp;
    }
    const byLabel = a.label.localeCompare(b.label);
    if (byLabel !== 0) {
      return byLabel;
    }
    return a.id.localeCompare(b.id);
  });
}

export function getNextOpponentId(primaryId: string, list: ModelInfo[]) {
  if (list.length < 2) {
    return "";
  }
  const i = list.findIndex((m) => m.id === primaryId);
  if (i >= 0 && i + 1 < list.length) {
    const next = list[i + 1];
    if (next.id !== primaryId) {
      return next.id;
    }
  }
  return list.find((m) => m.id !== primaryId)?.id ?? "";
}
