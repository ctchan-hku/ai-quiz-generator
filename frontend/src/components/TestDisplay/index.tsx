import { useTestBattleScreen } from "@/hooks/useTestBattleScreen";
import { useTestReviewScreen } from "@/hooks/useTestReviewScreen";
import { TestBattleView } from "./battle/TestBattleView";
import { TestReviewView } from "./review/TestReviewView";
import type { TestDisplayProps } from "./types";

export type { TestDisplayProps } from "./types";

export function TestDisplay(props: TestDisplayProps) {
  if (props.mode === "battle") {
    return <TestDisplayBattle {...props} />;
  }
  return <TestDisplayReview {...props} />;
}

function TestDisplayBattle(
  props: Extract<TestDisplayProps, { mode: "battle" }>,
) {
  const { battle, topic, pipelineVersion, models, onPickWinner } = props;
  const screen = useTestBattleScreen({
    battle,
    topic,
    pipelineVersion,
    models,
  });
  return <TestBattleView screen={screen} onPickWinner={onPickWinner} />;
}

function TestDisplayReview(
  props: Extract<TestDisplayProps, { mode: "review" }>,
) {
  const screen = useTestReviewScreen(props);
  return <TestReviewView {...props} screen={screen} />;
}
