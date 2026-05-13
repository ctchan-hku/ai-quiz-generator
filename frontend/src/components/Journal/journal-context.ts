import { createContext } from "react";

export interface JournalContextValue {
  /** Call after persisting a new quiz to local journal storage so listeners can refresh. */
  notifyJournalRecorded: () => void;
  /** Register a callback; returns unsubscribe. */
  subscribeToJournalRecorded: (callback: () => void) => () => void;
}

export const JournalContext = createContext<JournalContextValue | null>(null);
