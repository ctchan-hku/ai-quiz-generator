import type {
  GenerateTestResponse,
  MultipleChoiceQuestion,
} from "../api/contracts";
import type { VersionedTestReview } from "../types/test-machine";

export function versionedTestReviewFromResponse(
  response: GenerateTestResponse,
): VersionedTestReview {
  return {
    generation: response,
    questionVersions: response.questions.map((q) => [q]),
    selectedVersionIndex: response.questions.map(() => 0),
  };
}

export function selectedQuestion(
  review: VersionedTestReview,
  index: number,
): MultipleChoiceQuestion {
  return review.questionVersions[index][review.selectedVersionIndex[index]];
}

export function appendQuestionVersion(
  review: VersionedTestReview,
  index: number,
  question: MultipleChoiceQuestion,
): VersionedTestReview {
  const questionVersions = review.questionVersions.map((arr, i) =>
    i === index ? [...arr, question] : arr,
  );
  const selectedVersionIndex = review.selectedVersionIndex.map((s, i) =>
    i === index ? questionVersions[i].length - 1 : s,
  );
  return { ...review, questionVersions, selectedVersionIndex };
}

export function selectQuestionVersion(
  review: VersionedTestReview,
  index: number,
  selected: number,
): VersionedTestReview | null {
  const slot = review.questionVersions[index];
  if (selected < 0 || selected >= slot.length) return null;
  const selectedVersionIndex = review.selectedVersionIndex.map((s, i) =>
    i === index ? selected : s,
  );
  return { ...review, selectedVersionIndex };
}

export function testOutputFromReview(
  review: VersionedTestReview,
): GenerateTestResponse {
  return {
    model_used: review.generation.model_used,
    cost_usd: review.generation.cost_usd,
    questions: review.questionVersions.map((_, i) =>
      selectedQuestion(review, i),
    ),
  };
}
