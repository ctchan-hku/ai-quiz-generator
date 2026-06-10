export function getGearApiBaseUrl(): string {
  return import.meta.env.VITE_GEAR_API_BASE_URL ?? "/gear-api";
}
