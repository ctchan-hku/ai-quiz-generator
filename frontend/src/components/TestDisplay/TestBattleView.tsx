import type { GenerateTestResponse, ModelInfo } from "@/api/contracts";
import { pipelineVersionCaption } from "@/config/test-form";
import { formatEstimatedCostUsd } from "@/lib/format-usd";
import type { TestBattle } from "@/lib/test-machine/types";

import { BattleOpponentCarousel } from "./BattleOpponentCarousel";
import { TestQuestionCard } from "./TestQuestionCard";

export interface TestBattleViewProps {
  battle: TestBattle;
  topic: string;
  pipelineVersion: 1 | 2;
  models: ModelInfo[];
  onPickWinner: (side: "left" | "right") => void;
}

function labelForModel(models: ModelInfo[], modelId: string) {
  return models.find((m) => m.id === modelId)?.label ?? modelId;
}

function BattleTestQuestions({ test }: { test: GenerateTestResponse }) {
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4">
      {test.questions.map((q, qIdx) => (
        <TestQuestionCard key={qIdx} questionIndex={qIdx} question={q} />
      ))}
    </div>
  );
}

export function TestBattleView({
  battle,
  topic,
  pipelineVersion,
  models,
  onPickWinner,
}: TestBattleViewProps) {
  const { left: leftTest, right: rightTest } = battle;

  const leftTab = {
    roleLabel: "Left",
    modelLabel: labelForModel(models, leftTest.modelUsed),
    estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(leftTest.costUsd)}`,
  };
  const rightTab = {
    roleLabel: "Right",
    modelLabel: labelForModel(models, rightTest.modelUsed),
    estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(rightTest.costUsd)}`,
  };

  const topicLine =
    topic.trim() !== "" ? (
      <p className="mb-0 mt-0 text-sm text-foreground">
        <span className="font-semibold">Topic: </span>
        {topic.trim()}
      </p>
    ) : null;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        {topicLine}
        <p className="mb-0 mt-0 text-sm text-muted-foreground">
          <span className="font-semibold text-foreground">
            Generation pipeline:{" "}
          </span>
          {pipelineVersionCaption(pipelineVersion)}
        </p>
      </div>

      <BattleOpponentCarousel
        leftTab={leftTab}
        rightTab={rightTab}
        leftPane={<BattleTestQuestions test={leftTest} />}
        rightPane={<BattleTestQuestions test={rightTest} />}
        onConfirmSelection={onPickWinner}
      />
    </div>
  );
}
