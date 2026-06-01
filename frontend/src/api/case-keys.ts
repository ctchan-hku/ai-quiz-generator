function snakeCaseKey(key: string): string {
  return key.replace(/[A-Z]/g, (char) => `_${char.toLowerCase()}`);
}

function camelCaseKey(key: string): string {
  return key.replace(/_([a-z])/g, (_, char: string) => char.toUpperCase());
}

function mapObjectKeys<T>(value: T, mapKey: (key: string) => string): T {
  if (Array.isArray(value)) {
    return value.map((item) => mapObjectKeys(item, mapKey)) as T;
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, nested]) => [
        mapKey(key),
        mapObjectKeys(nested, mapKey),
      ]),
    ) as T;
  }
  return value;
}

/** Deep-convert object keys from camelCase to snake_case for JSON request bodies. */
export function toSnakeCaseKeys<T>(value: T): T {
  return mapObjectKeys(value, snakeCaseKey);
}

/** Deep-convert object keys from snake_case to camelCase for JSON response bodies. */
export function toCamelCaseKeys<T>(value: T): T {
  return mapObjectKeys(value, camelCaseKey);
}
