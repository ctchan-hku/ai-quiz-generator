/// <reference types="vite/client" />

export type AppMode = "dev" | "prod";

export const HTTP_CLIENT_TIMEOUT_MS = 600000;
export const QUERY_DEFAULT_RETRY = 1;
export const MUTATION_DEFAULT_RETRY = 0;

export const GEAR_API_PROXY_PATH = "/gear-api";
export const APP_API_DEV_TARGET = "http://127.0.0.1:8080";
export const GEAR_API_DEV_TARGET = "http://127.0.0.1:4000";

function normalizeOrigin(url: string | undefined): string {
  return url?.replace(/\/$/, "") ?? "";
}

export function getAppApiBaseUrl(): string {
  return normalizeOrigin(import.meta.env.VITE_API_BASE_URL);
}

export function getGearApiBaseUrl(): string {
  const direct = normalizeOrigin(import.meta.env.VITE_GEAR_API_URL);
  return direct || GEAR_API_PROXY_PATH;
}
