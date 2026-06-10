import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import { mergeConfig } from "vitest/config";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// https://vite.dev/config/
const viteConfig = defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      // When VITE_API_BASE_URL is unset, the app uses relative /api/* and this forwards to FastAPI.
      "/api": {
        target: "http://127.0.0.1:8080",
        changeOrigin: true,
      },
      // CMS auth (gi-2.0-backend). Used when VITE_CMS_API_BASE_URL is unset.
      "/cms-api": {
        target: "http://127.0.0.1:4000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/cms-api/, ""),
      },
    },
  },
});

export default mergeConfig(viteConfig, {
  test: {
    environment: "jsdom",
  },
});
