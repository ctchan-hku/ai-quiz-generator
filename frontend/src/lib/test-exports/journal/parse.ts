/** Pure parse and migrate of export journal JSON. No localStorage or DOM. */

import type { TestFormConfig } from "@/config/test-form";
import {
  EXPORT_JOURNAL_SCHEMA_VERSION,
  type ExportJournal,
  type ExportTestRecord,
} from "./types";

const LEGACY_EXPORT_JOURNAL_SCHEMA_VERSIONS = [9, 10] as const;

export function emptyJournal(): ExportJournal {
  return {
    schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
    updatedAt: new Date().toISOString(),
    tests: [],
  };
}

export type DeserializeJournalResult = {
  journal: ExportJournal;
  /** True when loaded data was migrated and should be written back to storage. */
  needsPersist: boolean;
};

export function deserializeJournal(raw: unknown): DeserializeJournalResult {
  if (!raw || typeof raw !== "object") {
    return { journal: emptyJournal(), needsPersist: false };
  }
  const o = raw as Record<string, unknown>;
  const schemaVersion = o.schemaVersion;
  if (
    (schemaVersion !== EXPORT_JOURNAL_SCHEMA_VERSION &&
      !LEGACY_EXPORT_JOURNAL_SCHEMA_VERSIONS.includes(
        schemaVersion as (typeof LEGACY_EXPORT_JOURNAL_SCHEMA_VERSIONS)[number],
      )) ||
    !Array.isArray(o.tests)
  ) {
    return { journal: emptyJournal(), needsPersist: false };
  }
  const tests = o.tests
    .map(parseExportTestRecord)
    .filter((record): record is ExportTestRecord => record != null);
  const journal: ExportJournal = {
    schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
    updatedAt:
      typeof o.updatedAt === "string"
        ? o.updatedAt
        : new Date().toISOString(),
    tests,
  };
  return {
    journal,
    needsPersist: schemaVersion !== EXPORT_JOURNAL_SCHEMA_VERSION,
  };
}

function parseExportTestRecord(raw: unknown): ExportTestRecord | null {
  if (!raw || typeof raw !== "object") return null;
  const record = raw as Record<string, unknown>;
  const formConfig = parseFormConfig(
    record.formConfig ?? record.testFormConfig ?? record.generationRequest,
  );
  if (formConfig == null) return null;
  if (
    typeof record.exportedAt !== "string" ||
    typeof record.modelUsed !== "string" ||
    typeof record.costUsd !== "number" ||
    !Array.isArray(record.questions)
  ) {
    return null;
  }
  return {
    exportedAt: record.exportedAt,
    modelUsed: record.modelUsed,
    costUsd: record.costUsd,
    questions: record.questions as ExportTestRecord["questions"],
    formConfig,
  };
}

function parseFormConfig(raw: unknown): TestFormConfig | null {
  if (!raw || typeof raw !== "object") return null;
  const config = raw as Record<string, unknown>;
  if (
    typeof config.topic !== "string" ||
    typeof config.numQuestions !== "number" ||
    !Array.isArray(config.models) ||
    (config.pipelineVersion !== 1 && config.pipelineVersion !== 2) ||
    !Array.isArray(config.fewShotExamples) ||
    !Array.isArray(config.userInstructions) ||
    typeof config.battleEnabled !== "boolean" ||
    !Array.isArray(config.selectedTestIds)
  ) {
    return null;
  }
  return {
    topic: config.topic,
    numQuestions: config.numQuestions,
    models: config.models as [string, string],
    pipelineVersion: config.pipelineVersion,
    fewShotExamples: config.fewShotExamples as string[],
    userInstructions: config.userInstructions as string[],
    battleEnabled: config.battleEnabled,
    selectedTestIds: config.selectedTestIds as string[],
  };
}
