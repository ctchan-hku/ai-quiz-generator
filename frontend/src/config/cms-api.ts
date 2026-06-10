export function getCmsApiBaseUrl(): string {
  return import.meta.env.VITE_CMS_API_BASE_URL ?? "/cms-api";
}
