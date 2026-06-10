import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    emptyOutDir: true,
    outDir: "jobagent/web/static/assets",
    rollupOptions: {
      input: "jobagent/web/frontend/main.tsx",
      output: {
        entryFileNames: "scout.js",
        chunkFileNames: "scout-[hash].js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith(".css")) {
            return "scout.css";
          }
          return "scout-[name][extname]";
        }
      }
    }
  }
});
