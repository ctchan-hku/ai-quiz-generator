import { useCallback, useEffect, useMemo, useState } from "react";
import type { ModelInfo } from "@/api/contracts";
import { usePagination } from "@/hooks/usePagination";
import {
  sortedModelsByCostColumn,
  costPerQuestionForPipeline,
  type CostPipelineColumn,
  type CostSortDirection,
} from "@/lib/model-board/cost-sort";
import {
  MODEL_BOARD_CONFIG,
  type ModelBoardRole,
} from "@/lib/model-board/config";

export type { ModelBoardRole };

const DEFAULT_MODELS_PER_PAGE = 5;

export function useModelBoard(params: {
  model: string;
  models: ModelInfo[];
  boardRole: ModelBoardRole;
  modelsPerPage?: number;
}) {
  const {
    model,
    models,
    boardRole,
    modelsPerPage = DEFAULT_MODELS_PER_PAGE,
  } = params;

  const [costColumn, setCostColumn] = useState<CostPipelineColumn>("v2");
  const [sortDirection, setSortDirection] = useState<CostSortDirection>("asc");

  const orderedModels = useMemo(
    () => sortedModelsByCostColumn(models, sortDirection, costColumn),
    [models, sortDirection, costColumn],
  );

  const modelsSortBasisKey = useMemo(
    () =>
      models
        .map(
          (m) =>
            `${m.id}\t${String(costPerQuestionForPipeline(m.id, costColumn))}`,
        )
        .join("\n"),
    [models, costColumn],
  );

  const { pageItems, nav, goToPage } = usePagination(
    orderedModels,
    modelsPerPage,
  );

  useEffect(() => {
    if (model.trim() === "" || models.length === 0) {
      return;
    }
    const ordered = sortedModelsByCostColumn(models, sortDirection, costColumn);
    const idx = ordered.findIndex((m) => m.id === model);
    if (idx < 0) {
      return;
    }
    const targetPage = Math.floor(idx / modelsPerPage);
    goToPage(targetPage);
  }, [
    model,
    sortDirection,
    costColumn,
    modelsSortBasisKey,
    goToPage,
    models,
    modelsPerPage,
  ]);

  const costLabelForModelId = useCallback(
    (modelId: string) => {
      const costUsd = costPerQuestionForPipeline(modelId, costColumn);
      return `$${costUsd}`;
    },
    [costColumn],
  );

  const toggleSort = useCallback(() => {
    setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
  }, []);

  const inputDomId = useCallback(
    (modelId: string) => `test-model-${boardRole}-${modelId}`,
    [boardRole],
  );

  const labelDomId = useCallback(
    (modelId: string) => `model-row-label-${boardRole}-${modelId}`,
    [boardRole],
  );

  return {
    costColumn,
    setCostColumn,
    sortDirection,
    toggleSort,
    pageItems,
    nav,
    roleUi: MODEL_BOARD_CONFIG[boardRole],
    pipelineSelectId: `model-board-cost-pipeline-${boardRole}`,
    costLabelForModelId,
    inputDomId,
    labelDomId,
  };
}
