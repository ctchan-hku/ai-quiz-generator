import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { appendTestRecord } from "./journal";

export interface RecordTestParams {
  test: GenerateTestResponse;
  commentsByIndex: string[];
  generationForm: TestFormConfig;
}

export function recordTestToJournal(params: RecordTestParams): void {
  const { test, commentsByIndex, generationForm } = params;

  appendTestRecord({
    exportedAt: new Date().toISOString(),
    modelUsed: test.modelUsed,
    costUsd: test.costUsd,
    questions: test.questions.map((q, i) => ({
      index: i,
      questionType: q.questionType,
      question: q.question,
      options: q.options,
      correctIndices: q.correctIndices,
      explanation: q.explanation,
      comment: (commentsByIndex[i] ?? "").trim(),
    })),
    generationRequest: generationForm,
  });
}
