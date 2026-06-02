import { useTestReviewScreen } from "@/hooks/useTestReviewScreen";
import type { TestDisplayProps } from "../types";
import { TestReviewView } from "./TestReviewView";

type ReviewProps = Extract<TestDisplayProps, { mode: "review" }>;

export function TestReviewContainer(props: ReviewProps) {
  const screen = useTestReviewScreen(props);
  return <TestReviewView {...props} screen={screen} />;
}
