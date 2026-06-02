import type { MultipleChoiceQuestion } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";

export const EXPORT_JOURNAL_SCHEMA_VERSION = 11 as const;
export const EXPORT_JOURNAL_STORAGE_KEY = "mastery-exec-test-export-journal";

export type ExportJournalSchemaVersion = typeof EXPORT_JOURNAL_SCHEMA_VERSION;

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
  schemaVersion: ExportJournalSchemaVersion;
  updatedAt: string;
  tests: ExportTestRecord[];
}
