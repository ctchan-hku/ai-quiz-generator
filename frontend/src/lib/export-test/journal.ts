import type { MultipleChoiceQuestion } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";

export const EXPORT_JOURNAL_SCHEMA_VERSION = 9 as const;
export const EXPORT_JOURNAL_STORAGE_KEY = "mastery-exec-test-export-journal";

export type ExportJournalSchemaVersion = typeof EXPORT_JOURNAL_SCHEMA_VERSION;

export type ExportedTestQuestion = MultipleChoiceQuestion & {
  index: number;
  comment: string;
};

export interface TestExportRecord {
  exportedAt: string;
  modelUsed: string;
  costUsd: number;
  questions: ExportedTestQuestion[];
  generationRequest: TestFormConfig;
}

export interface ExportJournal {
  schemaVersion: ExportJournalSchemaVersion;
  updatedAt: string;
  tests: TestExportRecord[];
}

export function loadJournal(): ExportJournal {
  try {
    const raw = localStorage.getItem(EXPORT_JOURNAL_STORAGE_KEY);
    if (raw == null || raw === "") return emptyJournal();
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object") return emptyJournal();
    const o = parsed as Record<string, unknown>;
    if (
      o.schemaVersion !== EXPORT_JOURNAL_SCHEMA_VERSION ||
      !Array.isArray(o.tests)
    ) {
      return emptyJournal();
    }
    return {
      schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
      updatedAt:
        typeof o.updatedAt === "string"
          ? o.updatedAt
          : new Date().toISOString(),
      tests: o.tests as TestExportRecord[],
    };
  } catch {
    return emptyJournal();
  }
}

export function appendTestRecord(record: TestExportRecord): ExportJournal {
  const journal = loadJournal();
  journal.tests.push(record);
  saveJournal(journal);
  return journal;
}

export function removeTestRecord(index: number): ExportJournal {
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
