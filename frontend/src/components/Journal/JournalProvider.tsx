import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  type ReactNode,
} from "react";

export interface JournalContextValue {
  /** Call after persisting a new quiz to local journal storage so listeners can refresh. */
  notifyJournalRecorded: () => void;
  /** Register a callback; returns unsubscribe. */
  subscribeToJournalRecorded: (callback: () => void) => () => void;
}

const JournalContext = createContext<JournalContextValue | null>(null);

export function JournalProvider({ children }: { children: ReactNode }) {
  const listenersRef = useRef(new Set<() => void>());

  const subscribeToJournalRecorded = useCallback((callback: () => void) => {
    listenersRef.current.add(callback);
    return () => {
      listenersRef.current.delete(callback);
    };
  }, []);

  const notifyJournalRecorded = useCallback(() => {
    listenersRef.current.forEach((listener) => {
      listener();
    });
  }, []);

  const value = useMemo(
    () => ({ notifyJournalRecorded, subscribeToJournalRecorded }),
    [notifyJournalRecorded, subscribeToJournalRecorded],
  );

  return (
    <JournalContext.Provider value={value}>{children}</JournalContext.Provider>
  );
}

export function useJournal(): JournalContextValue {
  const ctx = useContext(JournalContext);
  if (!ctx) {
    throw new Error("useJournal must be used within a JournalProvider");
  }
  return ctx;
}
