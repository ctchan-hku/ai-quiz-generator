import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { loadEnv } from "vite";
import { defineConfig, mergeConfig } from "vitest/config";

import { APP_API_PROXY_PATH, GEAR_API_PROXY_PATH } from "./src/api/config";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function requireProxyTarget(
  value: string | undefined,
  mode: string,
  variableName: string,
): string {
  if (value) {
    return value;
  }

  throw new Error(
    `Missing ${variableName} for vite --mode ${mode}. Copy frontend/.env.example to frontend/.env.${mode}.`,
  );
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const isDevServer = mode === "dev" || mode === "staging";

  const server = isDevServer
    ? (() => {
        const appApiTarget = requireProxyTarget(
          env.VITE_APP_API_PROXY_TARGET,
          mode,
          "VITE_APP_API_PROXY_TARGET",
        );
        const gearApiTarget = requireProxyTarget(
          env.VITE_GEAR_API_PROXY_TARGET,
          mode,
          "VITE_GEAR_API_PROXY_TARGET",
        );

        return {
          proxy: {
            [APP_API_PROXY_PATH]: {
              target: appApiTarget,
              changeOrigin: true,
            },
            [GEAR_API_PROXY_PATH]: {
              target: gearApiTarget,
              changeOrigin: true,
              secure: gearApiTarget.startsWith("https://"),
              rewrite: (requestPath: string) =>
                requestPath.replace(new RegExp(`^${GEAR_API_PROXY_PATH}`), ""),
            },
          },
        };
      })()
    : undefined;

  return mergeConfig(
    {
      plugins: [react(), tailwindcss()],
      resolve: {
        alias: {
          "@": path.resolve(__dirname, "./src"),
        },
      },
      ...(server ? { server } : {}),
    },
    {
      test: {
        environment: "jsdom",
      },
    },
  );
});
