import type { MultipleChoiceQuestion, TestResponse } from "../api/contracts";
import type { TestFormConfig } from "./test-machine";

/** Bump when the persisted JSON shape changes; `loadJournal` drops data from older versions. */
export const EXPORT_JOURNAL_SCHEMA_VERSION = 7 as const;

export type ExportJournalSchemaVersion = typeof EXPORT_JOURNAL_SCHEMA_VERSION;

/** One question as it appears in the downloaded JSON: full item plus order index and optional user notes. */
export type ExportedTestQuestion = MultipleChoiceQuestion & {
  index: number;
  comment: string;
};

export interface TestExportRecord {
  exported_at: string;
  topic: string;
  model_used: string;
  cost_usd: number;
  questions: ExportedTestQuestion[];
  /** Same payload as submit-time `TestFormConfig`. */
  generation_request?: TestFormConfig;
}

export interface ExportJournal {
  schema_version: ExportJournalSchemaVersion;
  updated_at: string;
  tests: TestExportRecord[];
}

export type BuildTestExportRecordParams = {
  test: TestResponse;
  topic: string;
  commentsByIndex: string[];
  generationForm?: TestFormConfig | null;
};
