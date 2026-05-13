import { useCallback, useMemo, useRef, type ReactNode } from "react";

import { JournalContext } from "./journal-context";

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
