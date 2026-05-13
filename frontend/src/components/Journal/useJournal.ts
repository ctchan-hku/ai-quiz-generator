import { useContext } from "react";

import { JournalContext, type JournalContextValue } from "./journal-context";

export function useJournal(): JournalContextValue {
  const ctx = useContext(JournalContext);
  if (!ctx) {
    throw new Error("useJournal must be used within a JournalProvider");
  }
  return ctx;
}
