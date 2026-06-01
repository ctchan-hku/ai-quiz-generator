import type {
  GenerateTestResponse,
  MultipleChoiceQuestion,
} from "@/api/contracts";

export interface TestVersionedReview {
  generation: GenerateTestResponse;
  questionVersions: MultipleChoiceQuestion[][];
  selectedVersionIndex: number[];
}

/** Wrap a generate response so each question can accumulate versions. */
export function toTestVersionedReview(
  response: GenerateTestResponse,
): TestVersionedReview {
  return {
    generation: response,
    questionVersions: response.questions.map((q) => [q]),
    selectedVersionIndex: response.questions.map(() => 0),
  };
}

/** Flatten a versioned review back to a generate response using selected versions. */
export function fromTestVersionedReview(
  review: TestVersionedReview,
): GenerateTestResponse {
  return {
    modelUsed: review.generation.modelUsed,
    costUsd: review.generation.costUsd,
    questions: review.questionVersions.map((_, i) =>
      selectedQuestion(review, i),
    ),
  };
}

export function selectedQuestion(
  review: TestVersionedReview,
  index: number,
): MultipleChoiceQuestion {
  return review.questionVersions[index][review.selectedVersionIndex[index]];
}

export function appendQuestionVersion(
  review: TestVersionedReview,
  index: number,
  question: MultipleChoiceQuestion,
): TestVersionedReview {
  const questionVersions = review.questionVersions.map((arr, i) =>
    i === index ? [...arr, question] : arr,
  );
  const selectedVersionIndex = review.selectedVersionIndex.map((s, i) =>
    i === index ? questionVersions[i].length - 1 : s,
  );
  return { ...review, questionVersions, selectedVersionIndex };
}

export function selectQuestionVersion(
  review: TestVersionedReview,
  index: number,
  selected: number,
): TestVersionedReview | null {
  const slot = review.questionVersions[index];
  if (selected < 0 || selected >= slot.length) return null;
  const selectedVersionIndex = review.selectedVersionIndex.map((s, i) =>
    i === index ? selected : s,
  );
  return { ...review, selectedVersionIndex };
}
