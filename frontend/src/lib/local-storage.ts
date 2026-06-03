type StorageEnvelope<T> = { version: number; value: T };

function ls(): Storage | null {
  return typeof window === "undefined" ? null : window.localStorage;
}

function parseRaw(raw: string | null): unknown {
  if (raw == null || raw === "") return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function loadVersioned<T>(
  key: string,
  version: number,
  migrate?: (old: unknown) => T | null,
): T | null {
  const parsed = parseRaw(ls()?.getItem(key) ?? null);
  if (!parsed || typeof parsed !== "object") return null;
  const o = parsed as Record<string, unknown>;

  if (typeof o.version === "number" && "value" in o) {
    const env = parsed as StorageEnvelope<T>;
    if (env.version === version) return env.value;
    const migrated = migrate?.(env.value);
    if (migrated != null) {
      saveVersioned(key, version, migrated);
      return migrated;
    }
    ls()?.removeItem(key);
    return null;
  }

  const legacyVersion =
    typeof o.schemaVersion === "number"
      ? o.schemaVersion
      : typeof o.v === "number"
        ? o.v
        : null;
  if (legacyVersion === version) {
    const value = parsed as T;
    saveVersioned(key, version, value);
    return value;
  }
  return null;
}

export function loadVersionedOrDefault<T>(
  key: string,
  version: number,
  fallback: T,
  migrate?: (old: unknown) => T | null,
): T {
  return loadVersioned(key, version, migrate) ?? fallback;
}

export function saveVersioned<T>(key: string, version: number, value: T): void {
  const envelope: StorageEnvelope<T> = { version, value };
  ls()?.setItem(key, JSON.stringify(envelope));
}

export function removeVersioned(key: string): void {
  ls()?.removeItem(key);
}
