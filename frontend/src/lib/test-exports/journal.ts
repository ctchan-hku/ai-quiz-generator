import type { MultipleChoiceQuestion } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";

export const EXPORT_JOURNAL_SCHEMA_VERSION = 11 as const;
export const EXPORT_JOURNAL_STORAGE_KEY = "mastery-exec-test-export-journal";

const LEGACY_EXPORT_JOURNAL_SCHEMA_VERSIONS = [9, 10] as const;

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

export function loadJournal(): ExportJournal {
  try {
    const raw = localStorage.getItem(EXPORT_JOURNAL_STORAGE_KEY);
    if (raw == null || raw === "") return emptyJournal();
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object") return emptyJournal();
    const o = parsed as Record<string, unknown>;
    const schemaVersion = o.schemaVersion;
    if (
      (schemaVersion !== EXPORT_JOURNAL_SCHEMA_VERSION &&
        !LEGACY_EXPORT_JOURNAL_SCHEMA_VERSIONS.includes(
          schemaVersion as (typeof LEGACY_EXPORT_JOURNAL_SCHEMA_VERSIONS)[number],
        )) ||
      !Array.isArray(o.tests)
    ) {
      return emptyJournal();
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
    if (schemaVersion !== EXPORT_JOURNAL_SCHEMA_VERSION) {
      saveJournal(journal);
    }
    return journal;
  } catch {
    return emptyJournal();
  }
}

export function appendExportTestRecord(
  record: ExportTestRecord,
): ExportJournal {
  const journal = loadJournal();
  journal.tests.push(record);
  saveJournal(journal);
  return journal;
}

export function removeExportTestRecord(index: number): ExportJournal {
  const journal = loadJournal();
  journal.tests.splice(index, 1);
  saveJournal(journal);
  return journal;
}

export function clearJournal(): void {
  localStorage.removeItem(EXPORT_JOURNAL_STORAGE_KEY);
}

export function downloadJournalFile(
  journal: ExportJournal,
  filename = "test-export-journal.json",
): void {
  const json = JSON.stringify(journal, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
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
    questions: record.questions as ExportTestQuestion[],
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

function saveJournal(journal: ExportJournal): void {
  const next: ExportJournal = {
    ...journal,
    updatedAt: new Date().toISOString(),
  };
  try {
    localStorage.setItem(EXPORT_JOURNAL_STORAGE_KEY, JSON.stringify(next));
  } catch (e) {
    if (e instanceof DOMException && e.name === "QuotaExceededError") {
      throw new Error(
        "Storage full — clear the journal or free browser space.",
      );
    }
    throw e;
  }
}

function emptyJournal(): ExportJournal {
  return {
    schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
    updatedAt: new Date().toISOString(),
    tests: [],
  };
}
