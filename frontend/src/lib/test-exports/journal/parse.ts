/** Envelope parse for export journal JSON. Records are trusted (app is the only writer). */

import {
  EXPORT_JOURNAL_SCHEMA_VERSION,
  type ExportJournal,
  type ExportTestRecord,
} from "./types";

export function emptyJournal(): ExportJournal {
  return {
    schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
    updatedAt: new Date().toISOString(),
    tests: [],
  };
}

export function deserializeJournal(raw: unknown): ExportJournal {
  if (!raw || typeof raw !== "object") {
    return emptyJournal();
  }
  const o = raw as Record<string, unknown>;
  if (
    o.schemaVersion !== EXPORT_JOURNAL_SCHEMA_VERSION ||
    !Array.isArray(o.tests)
  ) {
    return emptyJournal();
  }
  return {
    schemaVersion: EXPORT_JOURNAL_SCHEMA_VERSION,
    updatedAt:
      typeof o.updatedAt === "string" ? o.updatedAt : new Date().toISOString(),
    tests: o.tests as ExportTestRecord[],
  };
}
