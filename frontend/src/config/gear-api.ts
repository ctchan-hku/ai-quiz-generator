/// <reference types="vite/client" />

export const GEAR_API_PROXY_PATH = "/gear-api";

export const GEAR_API_DEFAULT_URL = "http://127.0.0.1:4000";

export function resolveGearApiProxyTarget(envUrl: string | undefined): string {
  return envUrl?.replace(/\/$/, "") || GEAR_API_DEFAULT_URL;
}

export function getGearApiBaseUrl(): string {
  if (import.meta.env.DEV) {
    return GEAR_API_PROXY_PATH;
  }

  const url = import.meta.env.VITE_GEAR_API_URL;
  if (!url) {
    throw new Error("VITE_GEAR_API_URL is required for production builds");
  }

  return url.replace(/\/$/, "");
}
