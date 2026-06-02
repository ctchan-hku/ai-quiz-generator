import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { appendExportTestRecord } from "./journal";

export interface RecordExportTestParams {
  test: GenerateTestResponse;
  commentsByIndex: string[];
  formConfig: TestFormConfig;
}

export function recordExportTestToJournal(
  params: RecordExportTestParams,
): void {
  const { test, commentsByIndex, formConfig } = params;

  appendExportTestRecord({
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
    formConfig,
  });
}
