/** Trigger a browser download of a journal JSON file. DOM side effects only. */

import type { ExportJournal } from "./types";

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
