/** Browser localStorage for the export journal. Side effects only. */

import { deserializeJournal, emptyJournal } from "./parse";
import type { ExportJournal, ExportTestRecord } from "./types";
import { EXPORT_JOURNAL_STORAGE_KEY } from "./types";

export type { ExportJournal, ExportTestRecord } from "./types";

export function loadJournal(): ExportJournal {
  try {
    const raw = localStorage.getItem(EXPORT_JOURNAL_STORAGE_KEY);
    if (raw == null || raw === "") return emptyJournal();
    const parsed = JSON.parse(raw) as unknown;
    const { journal, needsPersist } = deserializeJournal(parsed);
    if (needsPersist) {
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
