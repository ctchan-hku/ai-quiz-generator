import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { loadEnv } from "vite";
import { defineConfig, mergeConfig } from "vitest/config";

import {
  APP_API_DEV_TARGET,
  GEAR_API_PROXY_PATH,
  resolveGearApiProxyTarget,
} from "./src/config/api.constants";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode === "prod" ? "prod" : "dev", process.cwd(), "VITE_");
  const gearApiTarget = resolveGearApiProxyTarget(env.VITE_GEAR_API_URL);

  return mergeConfig(
    {
      plugins: [react(), tailwindcss()],
      resolve: {
        alias: {
          "@": path.resolve(__dirname, "./src"),
        },
      },
      server: {
        proxy: {
          "/api": {
            target: APP_API_DEV_TARGET,
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
      },
    },
    {
      test: {
        environment: "jsdom",
        env: {
          MODE: "dev",
          VITE_API_BASE_URL: "",
          VITE_GEAR_API_URL: "",
        },
      },
    },
  );
});
