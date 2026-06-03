import type { MultipleChoiceQuestion } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";

export type ExportTestQuestion = MultipleChoiceQuestion & {
  index: number;
  comment: string;
};

export interface ExportTestRecord {
  exportedAt: string;
  modelUsed: string;
  costUsd: number;
  questions: ExportTestQuestion[];
  formConfig: TestFormConfig;
}

export interface ExportJournal {
  updatedAt: string;
  tests: ExportTestRecord[];
}
