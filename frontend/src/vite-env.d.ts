/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly MODE: "dev" | "prod";
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_GEAR_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
