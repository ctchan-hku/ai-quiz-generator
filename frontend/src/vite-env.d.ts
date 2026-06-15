/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly MODE: "dev" | "staging" | "prod";
  readonly VITE_APP_API_PROXY_TARGET?: string;
  readonly VITE_GEAR_API_PROXY_TARGET?: string;
  readonly VITE_WORKSPACE_ENABLED?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
