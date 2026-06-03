/** Shared browser localStorage read/write. Domain modules supply parse only. */

function storage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage;
}

function readRaw(key: string): string | null {
  const raw = storage()?.getItem(key);
  if (raw == null || raw === "") {
    return null;
  }
  return raw;
}

export function loadFromLocalStorage<T>(
  key: string,
  parse: (parsed: unknown) => T,
  fallback: T,
): T {
  try {
    const raw = readRaw(key);
    if (raw === null) {
      return fallback;
    }
    return parse(JSON.parse(raw) as unknown);
  } catch {
    return fallback;
  }
}

export type SaveToLocalStorageOptions = {
  onQuotaExceeded?: "ignore" | "throw";
  quotaMessage?: string;
};

export function saveToLocalStorage(
  key: string,
  value: unknown,
  options?: SaveToLocalStorageOptions,
): void {
  const s = storage();
  if (!s) {
    return;
  }
  try {
    s.setItem(key, JSON.stringify(value));
  } catch (e) {
    if (
      options?.onQuotaExceeded === "throw" &&
      e instanceof DOMException &&
      e.name === "QuotaExceededError"
    ) {
      throw new Error(
        options.quotaMessage ??
          "Storage full — free browser space or clear saved data.",
      );
    }
  }
}

export function removeFromLocalStorage(key: string): void {
  storage()?.removeItem(key);
}
