import { useTestBattleScreen } from "@/hooks/useTestBattleScreen";
import type { TestDisplayProps } from "../types";
import { TestBattleView } from "./TestBattleView";

type BattleProps = Extract<TestDisplayProps, { mode: "battle" }>;

export function TestBattleContainer({
  battle,
  topic,
  pipelineVersion,
  models,
  onPickWinner,
}: BattleProps) {
  const screen = useTestBattleScreen({
    battle,
    topic,
    pipelineVersion,
    models,
  });

  return <TestBattleView screen={screen} onPickWinner={onPickWinner} />;
}
