/// <reference types="vite/client" />

import {
  GEAR_API_PROXY_PATH,
  normalizeEnvOrigin,
  type AppMode,
} from "./origins";

export type { AppMode };

function requireEnv(name: "VITE_API_BASE_URL" | "VITE_GEAR_API_URL"): string {
  const value = normalizeEnvOrigin(import.meta.env[name]);
  if (!value) {
    throw new Error(`${name} is required when MODE=prod`);
  }
  return value;
}

/** Base URL for this app's FastAPI backend (`/api/*`). */
export function getAppApiBaseUrl(): string {
  if (import.meta.env.MODE === "dev") {
    return "";
  }
  return requireEnv("VITE_API_BASE_URL");
}

/** Base URL for Gear authentication (`/api/authentication/*`). */
export function getGearApiBaseUrl(): string {
  if (import.meta.env.DEV) {
    return GEAR_API_PROXY_PATH;
  }
  return requireEnv("VITE_GEAR_API_URL");
}
