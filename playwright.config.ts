import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/ui",
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  reporter: [
    ["list"],
    ["json", { outputFile: "qa-artifacts/playwright/results.json" }],
    ["html", { outputFolder: "qa-artifacts/playwright/report", open: "never" }]
  ],
  use: {
    baseURL: "http://127.0.0.1:4173",
    headless: true,
    actionTimeout: 10_000,
    navigationTimeout: 30_000
  },
  webServer: {
    command: "python3 -m http.server 4173",
    port: 4173,
    reuseExistingServer: true
  }
});
