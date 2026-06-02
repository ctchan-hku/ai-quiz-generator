import { TestBattleContainer } from "./battle/TestBattleContainer";
import { TestReviewContainer } from "./review/TestReviewContainer";
import type { TestDisplayProps } from "./types";

export type { TestDisplayProps } from "./types";

export function TestDisplay(props: TestDisplayProps) {
  if (props.mode === "battle") {
    return <TestBattleContainer {...props} />;
  }

  return <TestReviewContainer {...props} />;
}
