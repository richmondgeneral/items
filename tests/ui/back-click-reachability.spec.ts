import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

/**
 * Back-side click reachability under iridescent tilt.
 *
 * The bug this guards against: when the back face has a 3D rotateX/rotateY
 * tilt applied (hover-driven iridescent finish), `.flip-card`'s untransformed
 * plane can sit IN FRONT of the now-tilted `.card-back` in 3D space. Hit-
 * testing at the button's visible position then returns `.flip-card`, not
 * the button — the click flips the card instead of triggering the link.
 *
 * Fix (in CSS): pointer-events:none on .flip-card, pointer-events:auto on
 * .card-face. The 3D container stops intercepting; only the actual faces
 * (which carry the button) receive clicks. Listeners on .flip-card still
 * fire via event bubbling.
 *
 * This test discovers iridescent cards (where the tilt is engaged) and asserts
 * that with the card flipped and hover-tilt active, the buy button (and other
 * interactive elements on the back) are the topmost hit-target at their own
 * bounding-rect center.
 */

function discoverIridescentSkus(): string[] {
  const cwd = process.cwd();
  return fs
    .readdirSync(cwd, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^RG-\d{4}$/.test(e.name))
    .map((e) => e.name)
    .filter((sku) => {
      const html = path.join(cwd, sku, "index.html");
      if (!fs.existsSync(html)) return false;
      const txt = fs.readFileSync(html, "utf-8");
      // Iridescent cards have the data-finish attribute AND an actual
      // buy-button anchor to test (sold-archive items omit the button —
      // matching on `class="buy-button"` rather than the bare substring
      // skips comments + script references).
      return (
        txt.includes('data-finish="iridescent"') &&
        /class="[^"]*\bbuy-button\b/.test(txt)
      );
    })
    .sort();
}

const SKUS = discoverIridescentSkus();

if (SKUS.length === 0) {
  test("back-click-reachability has no iridescent cards to check", () => {
    test.skip();
  });
} else {
  for (const sku of SKUS) {
    test(`${sku} buy button is hit-testable under tilt`, async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 900 });
      await page.goto(`/${sku}/`, { waitUntil: "domcontentloaded" });
      await expect(page.locator(".flip-card")).toBeVisible();

      // Flip to back via click (also exercises the event path through
      // pointer-events: auto on .card-face → bubbles to flip-card listener).
      await page.locator(".flip-card").click();
      await page.waitForTimeout(900); // settle the 0.8s flip animation

      // Engage hover tilt. Move into the card area; the iridescent controller
      // ramps --hov to 1 and writes --rx/--ry from cursor position.
      await page.mouse.move(700, 550);
      // Drive a few frames of mousemove for the easing to converge to ~1
      for (let i = 0; i < 30; i++) {
        await page.mouse.move(700 + (i % 2), 550); // tiny jitter to keep listener armed
        await page.waitForTimeout(16);
      }

      // Sanity-check that hover is engaged (would otherwise mask the bug).
      const hov = await page.evaluate(() => {
        const fc = document.querySelector(".flip-card") as HTMLElement;
        return parseFloat(fc.style.getPropertyValue("--hov") || "0");
      });
      expect(hov, "hover must be engaged for this test to be meaningful").toBeGreaterThan(0.5);

      // Now: at the buy button's center, hit-test should land on the button.
      const result = await page.evaluate(() => {
        const buy = document.querySelector(".buy-button") as HTMLElement;
        const r = buy.getBoundingClientRect();
        const el = document.elementFromPoint(
          r.left + r.width / 2,
          r.top + r.height / 2
        );
        return {
          tag: el?.tagName ?? null,
          className: el?.className ?? null,
          isButton: el === buy || el?.closest(".buy-button") === buy,
        };
      });

      expect(
        result.isButton,
        `expected buy-button at its own center; got ${result.tag}.${result.className}`
      ).toBe(true);
    });
  }
}
