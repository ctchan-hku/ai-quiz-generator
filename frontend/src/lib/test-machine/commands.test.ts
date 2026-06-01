import { describe, expect, it, vi, beforeEach } from "vitest";
import type { GenerateTestResponse } from "@/api/contracts";
import { testFormFieldDefaults } from "@/config/test-form";
import { runEditQuestion, runGenerateTest } from "./commands";

vi.mock("@/api", () => ({
  generateTest: vi.fn(),
  editQuestion: vi.fn(),
}));

import { editQuestion, generateTest } from "@/api";

const mockResponse: GenerateTestResponse = {
  modelUsed: "gpt-test",
  costUsd: 0.01,
  questions: [
    {
      questionType: "multiple_choice",
      question: "Q1?",
      options: ["A", "B"],
      correctIndices: [0],
      explanation: "",
    },
  ],
};

describe("runGenerateTest", () => {
  beforeEach(() => {
    vi.mocked(generateTest).mockReset();
  });

  it("single mode calls generateTest once", async () => {
    vi.mocked(generateTest).mockResolvedValue(mockResponse);
    const config = {
      ...testFormFieldDefaults,
      battleEnabled: false,
      models: ["gpt-test", ""] as [string, string],
    };
    const result = await runGenerateTest(config, new AbortController().signal);
    expect(generateTest).toHaveBeenCalledTimes(1);
    expect(result).toEqual({ mode: "single", payload: mockResponse });
  });

  it("battle mode calls generateTest twice in parallel", async () => {
    vi.mocked(generateTest).mockResolvedValue(mockResponse);
    const config = {
      ...testFormFieldDefaults,
      battleEnabled: true,
      models: ["model-a", "model-b"] as [string, string],
    };
    const result = await runGenerateTest(config, new AbortController().signal);
    expect(generateTest).toHaveBeenCalledTimes(2);
    expect(result.mode).toBe("battle");
    if (result.mode === "battle") {
      expect(result.payload.left).toEqual(mockResponse);
      expect(result.payload.right).toEqual(mockResponse);
    }
  });
});

describe("runEditQuestion", () => {
  beforeEach(() => {
    vi.mocked(editQuestion).mockReset();
  });

  it("trims comment and calls editQuestion", async () => {
    const editedQuestion = mockResponse.questions[0];
    vi.mocked(editQuestion).mockResolvedValue(editedQuestion);
    const result = await runEditQuestion(
      {
        index: 0,
        model: "gpt-test",
        topic: "Biology",
        question: editedQuestion,
        comment: "  fix wording  ",
      },
      new AbortController().signal,
    );
    expect(editQuestion).toHaveBeenCalledWith(
      {
        model: "gpt-test",
        topic: "Biology",
        question: editedQuestion,
        comment: "fix wording",
      },
      expect.any(AbortSignal),
    );
    expect(result).toEqual(editedQuestion);
  });
});
