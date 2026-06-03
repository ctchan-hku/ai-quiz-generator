import {
  loadVersionedOrDefault,
  removeVersioned,
  saveVersioned,
} from "@/lib/local-storage";
import type { ExportJournal, ExportTestRecord } from "./types";

const JOURNAL_KEY = "journal";
const JOURNAL_VERSION = 1;

export function emptyJournal(): ExportJournal {
  return {
    updatedAt: new Date().toISOString(),
    tests: [],
  };
}

function parseJournal(stored: ExportJournal): ExportJournal {
  if (!Array.isArray(stored.tests)) return emptyJournal();
  return {
    updatedAt:
      typeof stored.updatedAt === "string"
        ? stored.updatedAt
        : new Date().toISOString(),
    tests: stored.tests,
  };
}

export function loadJournal(): ExportJournal {
  return parseJournal(
    loadVersionedOrDefault(JOURNAL_KEY, JOURNAL_VERSION, emptyJournal()),
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
  removeVersioned(JOURNAL_KEY);
}

function saveJournal(journal: ExportJournal): void {
  try {
    saveVersioned(JOURNAL_KEY, JOURNAL_VERSION, {
      ...journal,
      updatedAt: new Date().toISOString(),
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "QuotaExceededError") {
      throw new Error(
        "Storage full — clear the journal or free browser space.",
      );
    }
    throw e;
  }
}
