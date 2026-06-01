import { describe, expect, it } from "vitest";
import type { GenerateTestResponse } from "@/api/contracts";
import {
  appendQuestionVersion,
  fromTestVersionedReview,
  selectQuestionVersion,
  toTestVersionedReview,
} from "./versioned-review";

const baseResponse: GenerateTestResponse = {
  modelUsed: "m1",
  costUsd: 0.5,
  questions: [
    {
      questionType: "multiple_choice",
      question: "Original?",
      options: ["A", "B"],
      correctIndices: [0],
      explanation: "",
    },
  ],
};

describe("toTestVersionedReview", () => {
  it("wraps each question in a single-version array", () => {
    const review = toTestVersionedReview(baseResponse);
    expect(review.questionVersions).toHaveLength(1);
    expect(review.questionVersions[0]).toHaveLength(1);
    expect(review.selectedVersionIndex).toEqual([0]);
  });
});

describe("appendQuestionVersion", () => {
  it("appends and selects the new version", () => {
    const review = toTestVersionedReview(baseResponse);
    const edited = {
      questionType: "multiple_choice" as const,
      question: "Edited?",
      options: ["A", "B"],
      correctIndices: [1],
      explanation: "",
    };
    const next = appendQuestionVersion(review, 0, edited);
    expect(next.questionVersions[0]).toHaveLength(2);
    expect(next.selectedVersionIndex[0]).toBe(1);
    expect(fromTestVersionedReview(next).questions[0].question).toBe("Edited?");
  });
});

describe("selectQuestionVersion", () => {
  it("returns null for out-of-range index", () => {
    const review = toTestVersionedReview(baseResponse);
    expect(selectQuestionVersion(review, 0, 99)).toBeNull();
  });
});
