import type { TestBattleScreen } from "@/hooks/useTestBattleScreen";

import { BattleOpponentCarousel } from "./BattleOpponentCarousel";
import { TestQuestionCard } from "../shared/TestQuestionCard";
import type { GenerateTestResponse } from "@/api/contracts";

export interface TestBattleViewProps {
  screen: TestBattleScreen;
  onPickWinner: (side: "left" | "right") => void;
}

function BattleTestQuestions({
  test,
  optionLabelsByQuestion,
}: {
  test: GenerateTestResponse;
  optionLabelsByQuestion: string[][];
}) {
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4">
      {test.questions.map((q, qIdx) => (
        <TestQuestionCard
          key={qIdx}
          questionIndex={qIdx}
          question={q}
          optionLabels={optionLabelsByQuestion[qIdx]}
        />
      ))}
    </div>
  );
}

export function TestBattleView({ screen, onPickWinner }: TestBattleViewProps) {
  const {
    leftTest,
    rightTest,
    leftTab,
    rightTab,
    leftOptionLabelsByQuestion,
    rightOptionLabelsByQuestion,
    pipelineCaption,
    topicTrimmed,
  } = screen;

  const topicLine =
    topicTrimmed !== "" ? (
      <p className="mb-0 mt-0 text-sm text-foreground">
        <span className="font-semibold">Topic: </span>
        {topicTrimmed}
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
          {pipelineCaption}
        </p>
      </div>

      <BattleOpponentCarousel
        leftTab={leftTab}
        rightTab={rightTab}
        leftPane={
          <BattleTestQuestions
            test={leftTest}
            optionLabelsByQuestion={leftOptionLabelsByQuestion}
          />
        }
        rightPane={
          <BattleTestQuestions
            test={rightTest}
            optionLabelsByQuestion={rightOptionLabelsByQuestion}
          />
        }
        onConfirmSelection={onPickWinner}
      />
    </div>
  );
}
