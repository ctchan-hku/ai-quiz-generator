import type {
  GenerateTestResponse,
  MultipleChoiceQuestion,
} from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";

export const EXPORT_JOURNAL_SCHEMA_VERSION = 9 as const;

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

export type BuildTestExportRecordParams = {
  test: GenerateTestResponse;
  commentsByIndex: string[];
  generationForm: TestFormConfig;
};

export const EXPORT_JOURNAL_STORAGE_KEY = "mastery-exec-test-export-journal";

function emptyJournal(): ExportJournal {
  return {
    schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
    updatedAt: new Date().toISOString(),
    tests: [],
  };
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

export function saveJournal(j: ExportJournal): void {
  const next: ExportJournal = {
    ...j,
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

export function appendTestRecord(record: TestExportRecord): ExportJournal {
  const j = loadJournal();
  j.tests.push(record);
  saveJournal(j);
  return j;
}

export function clearJournal(): void {
  localStorage.removeItem(EXPORT_JOURNAL_STORAGE_KEY);
}

function buildExportedTestQuestion(
  q: MultipleChoiceQuestion,
  index: number,
  comment: string,
): ExportedTestQuestion {
  return {
    index,
    questionType: q.questionType,
    question: q.question,
    options: q.options,
    correctIndices: q.correctIndices,
    explanation: q.explanation,
    comment: comment.trim(),
  };
}

export function removeTestRecord(index: number): ExportJournal {
  const j = loadJournal();
  j.tests.splice(index, 1);
  saveJournal(j);
  return j;
}

export function buildTestExportRecord(
  params: BuildTestExportRecordParams,
): TestExportRecord {
  const { test, commentsByIndex, generationForm } = params;

  return {
    exportedAt: new Date().toISOString(),
    modelUsed: test.modelUsed,
    costUsd: test.costUsd,
    questions: test.questions.map((q, i) =>
      buildExportedTestQuestion(q, i, commentsByIndex[i] ?? ""),
    ),
    generationRequest: generationForm,
  };
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
