import fs from "node:fs";
import path from "node:path";
import { expect, test, type Page } from "@playwright/test";

type Viewport = { name: "desktop" | "mobile"; width: number; height: number };

const VIEWPORTS: Viewport[] = [
  { name: "desktop", width: 1440, height: 1100 },
  { name: "mobile", width: 390, height: 844 }
];

const SCREENSHOT_ROOT = path.join("qa-artifacts", "screenshots");

function discoverSkus(): string[] {
  return fs
    .readdirSync(process.cwd(), { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^RG-\d{4}$/.test(entry.name))
    .filter((entry) => fs.existsSync(path.join(entry.name, "index.html")))
    .map((entry) => entry.name)
    .sort();
}

async function assertNoBrokenImages(page: Page): Promise<void> {
  const broken = await page.evaluate(() => {
    return Array.from(document.images)
      .filter((img) => !img.complete || img.naturalWidth === 0)
      .map((img) => img.getAttribute("src") || img.src);
  });
  expect(broken, `Broken images found: ${broken.join(", ")}`).toEqual([]);
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const hasOverflow = await page.evaluate(() => {
    const tolerance = 1;
    return document.documentElement.scrollWidth > window.innerWidth + tolerance;
  });
  expect(hasOverflow).toBeFalsy();
}

async function capture(page: Page, sku: string, viewport: string, side: "front" | "back"): Promise<void> {
  const outDir = path.join(SCREENSHOT_ROOT, sku);
  fs.mkdirSync(outDir, { recursive: true });
  const filePath = path.join(outDir, `${viewport}-${side}.png`);
  await page.screenshot({ path: filePath, fullPage: true });
}

async function flipCard(page: Page): Promise<void> {
  const card = page.locator(".flip-card").first();
  await card.click();
  await page.waitForTimeout(450);

  let flipped = await card.evaluate((el) => el.classList.contains("flipped"));
  if (!flipped) {
    await card.press("Enter");
    await page.waitForTimeout(450);
    flipped = await card.evaluate((el) => el.classList.contains("flipped"));
  }

  expect(flipped).toBeTruthy();
}

const skus = discoverSkus();

for (const sku of skus) {
  for (const viewport of VIEWPORTS) {
    test(`${sku} ${viewport.name} front`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto(`/${sku}/`, { waitUntil: "domcontentloaded" });

      const card = page.locator(".flip-card").first();
      await expect(card).toBeVisible();

      const buyButton = page.locator(".buy-button").first();
      await expect(buyButton).toBeVisible();
      const href = await buyButton.getAttribute("href");
      expect(href).toBeTruthy();
      expect(href).not.toBe("#");

      await page.waitForLoadState("networkidle");
      await assertNoBrokenImages(page);
      await assertNoHorizontalOverflow(page);
      await capture(page, sku, viewport.name, "front");
    });

    test(`${sku} ${viewport.name} back`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto(`/${sku}/`, { waitUntil: "domcontentloaded" });

      await flipCard(page);
      await page.waitForLoadState("networkidle");
      await assertNoBrokenImages(page);
      await assertNoHorizontalOverflow(page);
      await capture(page, sku, viewport.name, "back");
    });
  }
}
