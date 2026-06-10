export type AppMode = "dev" | "prod";

export const GEAR_API_PROXY_PATH = "/gear-api";

export const APP_API_DEV_TARGET = "http://127.0.0.1:8080";
export const GEAR_API_DEV_TARGET = "http://127.0.0.1:4000";

function normalizeOrigin(url: string | undefined): string {
  return url?.replace(/\/$/, "") ?? "";
}

/** Vite dev-server proxy target for Gear (vite.config only). */
export function resolveGearApiProxyTarget(envUrl: string | undefined): string {
  return normalizeOrigin(envUrl) || GEAR_API_DEV_TARGET;
}

export function normalizeEnvOrigin(url: string | undefined): string {
  return normalizeOrigin(url);
}
