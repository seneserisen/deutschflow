import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";
import { copyFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  plugins: [react(), { name: "copy-manifest", writeBundle() { copyFileSync(resolve(root, "manifest.json"), resolve(root, "dist/manifest.json")); } }],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        panel: resolve(root, "panel.html"),
        popup: resolve(root, "popup.html"),
        options: resolve(root, "options.html"),
        background: resolve(root, "src/background/index.ts"),
        selection: resolve(root, "src/content/injected.ts"),
      },
      output: {
        entryFileNames: "assets/[name].js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    globals: true,
  },
});
