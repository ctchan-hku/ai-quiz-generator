import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { appendTestRecord, buildTestExportRecord } from "./journal";

export interface RecordTestParams {
  test: GenerateTestResponse;
  commentsByIndex: string[];
  generationForm: TestFormConfig;
}

export function recordTestToJournal(params: RecordTestParams): void {
  const record = buildTestExportRecord({
    test: params.test,
    commentsByIndex: params.commentsByIndex,
    generationForm: params.generationForm,
  });
  appendTestRecord(record);
}
