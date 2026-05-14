import { expect, test } from "@playwright/test";

/**
 * Quick verification that :focus-visible correctly distinguishes
 * keyboard focus (outline shown) from mouse-click focus (outline hidden).
 * The mouse-click case is what the user reported on RG-0001 — a gold
 * outline that doesn't transform with the card's hover tilt.
 */
test("RG-0001 focus ring: mouse click → no outline; keyboard Tab → outline", async ({ page }) => {
  await page.goto("/RG-0001/", { waitUntil: "domcontentloaded" });
  const card = page.locator(".flip-card").first();
  await expect(card).toBeVisible();

  // Clear any pre-existing focus, then mouse-click the card.
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur?.());
  // Click outside first to clear focus, then click the card.
  await page.mouse.click(5, 5);
  await card.click();
  // The card immediately toggles .flipped on click; wait for the flip
  // animation so the outline (if any) is read in steady state.
  await page.waitForTimeout(900);

  const outlineAfterClick = await card.evaluate(
    (el) => getComputedStyle(el).outlineStyle
  );
  expect(outlineAfterClick, "mouse-click focus should NOT show outline").toBe("none");

  // Reset state: blur, un-flip, then keyboard-focus the card.
  await page.evaluate(() => {
    const c = document.querySelector(".flip-card") as HTMLElement;
    c.classList.remove("flipped");
    c.blur();
  });
  await page.keyboard.press("Tab");
  // Tab may land on the card or on a focusable element before it; keep
  // tabbing until .flip-card is focused (it has tabindex=0 and is the
  // only focusable element on the page besides .buy-button which lives
  // on the back face).
  for (let i = 0; i < 5; i++) {
    const focused = await page.evaluate(() =>
      document.activeElement?.classList.contains("flip-card")
    );
    if (focused) break;
    await page.keyboard.press("Tab");
  }
  const isCardFocused = await page.evaluate(() =>
    document.activeElement?.classList.contains("flip-card")
  );
  expect(isCardFocused, "card should receive keyboard focus").toBe(true);

  const outlineAfterTab = await card.evaluate(
    (el) => getComputedStyle(el).outlineStyle
  );
  expect(outlineAfterTab, "keyboard focus should show outline").toBe("solid");
});
