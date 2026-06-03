/** Browser localStorage for the export journal. Side effects only. */

import {
  loadFromLocalStorage,
  removeFromLocalStorage,
  saveToLocalStorage,
} from "@/lib/local-storage";
import { deserializeJournal, emptyJournal } from "./parse";
import type { ExportJournal, ExportTestRecord } from "./types";
import { EXPORT_JOURNAL_STORAGE_KEY } from "./types";

export type { ExportJournal, ExportTestRecord } from "./types";

export function loadJournal(): ExportJournal {
  return loadFromLocalStorage(
    EXPORT_JOURNAL_STORAGE_KEY,
    deserializeJournal,
    emptyJournal(),
  );
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
  removeFromLocalStorage(EXPORT_JOURNAL_STORAGE_KEY);
}

function saveJournal(journal: ExportJournal): void {
  const next: ExportJournal = {
    ...journal,
    updatedAt: new Date().toISOString(),
  };
  saveToLocalStorage(EXPORT_JOURNAL_STORAGE_KEY, next, {
    onQuotaExceeded: "throw",
    quotaMessage: "Storage full — clear the journal or free browser space.",
  });
}
