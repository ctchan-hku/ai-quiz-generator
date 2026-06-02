import { useMemo } from "react";
import type { ModelInfo } from "@/api/contracts";
import { pipelineVersionCaption } from "@/config/test-form";
import { formatEstimatedCostUsd } from "@/lib/display/format-usd";
import { optionLabel } from "@/lib/display/mc-option-label";
import { modelDisplayLabel } from "@/lib/model-board/model-label";
import type { TestBattle } from "@/hooks/useTestMachine";

export type TestBattleScreenProps = {
  battle: TestBattle;
  topic: string;
  pipelineVersion: 1 | 2;
  models: ModelInfo[];
};

export function useTestBattleScreen(props: TestBattleScreenProps) {
  const { battle, topic, pipelineVersion, models } = props;
  const { left: leftTest, right: rightTest } = battle;

  const leftTab = useMemo(
    () => ({
      roleLabel: "Left",
      modelLabel: modelDisplayLabel(models, leftTest.modelUsed),
      estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(leftTest.costUsd)}`,
    }),
    [models, leftTest.modelUsed, leftTest.costUsd],
  );

  const rightTab = useMemo(
    () => ({
      roleLabel: "Right",
      modelLabel: modelDisplayLabel(models, rightTest.modelUsed),
      estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(rightTest.costUsd)}`,
    }),
    [models, rightTest.modelUsed, rightTest.costUsd],
  );

  const leftOptionLabelsByQuestion = useMemo(
    () =>
      leftTest.questions.map((q) =>
        q.options.map((_, optIdx) => optionLabel(optIdx)),
      ),
    [leftTest],
  );

  const rightOptionLabelsByQuestion = useMemo(
    () =>
      rightTest.questions.map((q) =>
        q.options.map((_, optIdx) => optionLabel(optIdx)),
      ),
    [rightTest],
  );

  const pipelineCaption = pipelineVersionCaption(pipelineVersion);
  const topicTrimmed = topic.trim();

  return {
    leftTest,
    rightTest,
    leftTab,
    rightTab,
    leftOptionLabelsByQuestion,
    rightOptionLabelsByQuestion,
    pipelineCaption,
    topicTrimmed,
  };
}

export type TestBattleScreen = ReturnType<typeof useTestBattleScreen>;
