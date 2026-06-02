import { useCallback, type Dispatch, type SetStateAction } from "react";
import type { ModelInfo } from "@/api/contracts";
import { testFormFieldDefaults, type TestFormConfig } from "@/config/test-form";
import { getNextOpponentId } from "@/lib/model-board/cost-sort";

export function useBattleModeToggle({
  onFormConfigChange,
  availableModels,
}: {
  onFormConfigChange: Dispatch<SetStateAction<TestFormConfig>>;
  availableModels: ModelInfo[];
}) {
  const onBattleModeChange = useCallback(
    (next: boolean) => {
      onFormConfigChange((s) =>
        next
          ? {
              ...s,
              battleEnabled: true,
              models: [
                s.models[0],
                getNextOpponentId(s.models[0], availableModels),
              ],
            }
          : {
              ...s,
              battleEnabled: false,
              models: [s.models[0], testFormFieldDefaults.models[1]],
            },
      );
    },
    [onFormConfigChange, availableModels],
  );

  return { onBattleModeChange };
}
