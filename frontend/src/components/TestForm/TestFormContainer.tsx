import { useBattleModeToggle } from "@/hooks/useBattleModeToggle";
import { TestForm, type TestFormProps } from "./index";

type TestFormContainerProps = Omit<TestFormProps, "onBattleModeChange">;

export function TestFormContainer({
  onFormConfigChange,
  availableModels,
  ...props
}: TestFormContainerProps) {
  const { onBattleModeChange } = useBattleModeToggle({
    onFormConfigChange,
    availableModels,
  });

  return (
    <TestForm
      {...props}
      onFormConfigChange={onFormConfigChange}
      availableModels={availableModels}
      onBattleModeChange={onBattleModeChange}
    />
  );
}
