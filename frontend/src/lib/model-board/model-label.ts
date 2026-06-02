import type { ModelInfo } from "@/api/contracts";

export function modelDisplayLabel(
  models: ModelInfo[] | undefined,
  modelId: string,
): string {
  if (!models?.length) return modelId;
  return models.find((m) => m.id === modelId)?.label ?? modelId;
}
