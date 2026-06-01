import { TestBattleView } from "./TestBattleView";
import { TestReviewView } from "./TestReviewView";
import type { TestDisplayProps } from "./types";

export type { TestDisplayProps } from "./types";

export function TestDisplay(props: TestDisplayProps) {
  if (props.mode === "battle") {
    const { battle, topic, pipelineVersion, models, onPickWinner } = props;
    return (
      <TestBattleView
        battle={battle}
        topic={topic}
        pipelineVersion={pipelineVersion}
        models={models}
        onPickWinner={onPickWinner}
      />
    );
  }

  return <TestReviewView {...props} />;
}
