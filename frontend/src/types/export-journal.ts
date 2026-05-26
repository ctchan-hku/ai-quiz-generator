import type {
  MultipleChoiceQuestion,
  GenerateTestResponse,
} from "../api/contracts";
import type { TestFormConfig } from "./test-machine";

export const EXPORT_JOURNAL_SCHEMA_VERSION = 8 as const;

export type ExportJournalSchemaVersion = typeof EXPORT_JOURNAL_SCHEMA_VERSION;

export type ExportedTestQuestion = MultipleChoiceQuestion & {
  index: number;
  comment: string;
};

export interface TestExportRecord {
  exported_at: string;
  model_used: string;
  cost_usd: number;
  questions: ExportedTestQuestion[];
  generation_request: TestFormConfig;
}

export interface ExportJournal {
  schema_version: ExportJournalSchemaVersion;
  updated_at: string;
  tests: TestExportRecord[];
}

export type BuildTestExportRecordParams = {
  test: GenerateTestResponse;
  commentsByIndex: string[];
  generationForm: TestFormConfig;
};
