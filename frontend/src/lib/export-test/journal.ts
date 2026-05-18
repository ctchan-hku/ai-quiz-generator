import type { MultipleChoiceQuestion } from "../../api";
import {
  EXPORT_JOURNAL_SCHEMA_VERSION,
  type BuildTestExportRecordParams,
  type ExportJournal,
  type ExportedTestQuestion,
  type TestExportRecord,
} from "../../types/export-journal";

export const EXPORT_JOURNAL_STORAGE_KEY = "mastery-exec-test-export-journal";

export type {
  BuildTestExportRecordParams,
  ExportJournal,
  ExportedTestQuestion,
  TestExportRecord,
} from "../../types/export-journal";

function emptyJournal(): ExportJournal {
  return {
    schema_version: EXPORT_JOURNAL_SCHEMA_VERSION,
    updated_at: new Date().toISOString(),
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
      o.schema_version !== EXPORT_JOURNAL_SCHEMA_VERSION ||
      !Array.isArray(o.tests)
    ) {
      return emptyJournal();
    }
    return {
      schema_version: EXPORT_JOURNAL_SCHEMA_VERSION,
      updated_at:
        typeof o.updated_at === "string"
          ? o.updated_at
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
    updated_at: new Date().toISOString(),
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
    question_type: q.question_type,
    question: q.question,
    options: q.options,
    correct_indices: q.correct_indices,
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
  const { test, topic, commentsByIndex, generationForm } = params;

  const record: TestExportRecord = {
    exported_at: new Date().toISOString(),
    topic: topic.trim(),
    model_used: test.model_used,
    cost_usd: test.cost_usd,
    questions: test.questions.map((q, i) =>
      buildExportedTestQuestion(q, i, commentsByIndex[i] ?? ""),
    ),
  };

  if (generationForm != null) {
    record.generation_request = generationForm;
  }

  return record;
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
