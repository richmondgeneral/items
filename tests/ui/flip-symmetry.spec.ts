import fs from "node:fs";
import path from "node:path";
import { expect, test, type Page } from "@playwright/test";

/**
 * Hover-tilt symmetry test for iridescent cards.
 *
 * The iridescent finish (see CSS comment block in RG-XXXX/index.html) tracks
 * the cursor and tilts the card via CSS variables that BOTH .card-front and
 * .card-back inherit. The bug fixed in PR #16: the back face negated --ry,
 * which combined with .flip-card.flipped's rotateY(180) to produce an
 * opposite tilt instead of a matching one.
 *
 * Strategy: set --rx and --ry directly on .flip-card to known values
 * (bypassing the rAF easing controller, which makes the test deterministic
 * and ~50x faster), read the computed transforms on both faces, then
 * verify that rotateY(180) × cardBack.transform equals cardFront.transform.
 *
 * The bug's signal is a SIGN FLIP on matrix entries — diff of ~0.3 in
 * matrix[2]/matrix[8]. Our tolerance of 1e-6 gives ~5 orders of magnitude
 * of safety margin while still catching float drift if it appears.
 */

type Matrix16 = number[];

const ROTATE_Y_180: Matrix16 = [
  -1, 0,  0, 0,
   0, 1,  0, 0,
   0, 0, -1, 0,
   0, 0,  0, 1,
];

function discoverIridescentSkus(): string[] {
  const cwd = process.cwd();
  return fs
    .readdirSync(cwd, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^RG-\d{4}$/.test(e.name))
    .map((e) => e.name)
    .filter((sku) => {
      const html = path.join(cwd, sku, "index.html");
      if (!fs.existsSync(html)) return false;
      return fs.readFileSync(html, "utf-8").includes('data-finish="iridescent"');
    })
    .sort();
}

function parseTransform(s: string): Matrix16 {
  if (s === "none") {
    return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  }
  const m = s.match(/matrix(3d)?\(([^)]+)\)/);
  if (!m) throw new Error(`Cannot parse transform: ${s}`);
  const vals = m[2].split(",").map(parseFloat);
  if (vals.length === 6) {
    const [a, b, c, d, e, f] = vals;
    return [a, c, 0, e, b, d, 0, f, 0, 0, 1, 0, 0, 0, 0, 1];
  }
  // matrix3d() is column-major; convert to row-major for easier multiplication.
  return [
    vals[0], vals[4], vals[8],  vals[12],
    vals[1], vals[5], vals[9],  vals[13],
    vals[2], vals[6], vals[10], vals[14],
    vals[3], vals[7], vals[11], vals[15],
  ];
}

function multiply(A: Matrix16, B: Matrix16): Matrix16 {
  const r = new Array(16).fill(0);
  for (let i = 0; i < 4; i++)
    for (let j = 0; j < 4; j++)
      for (let k = 0; k < 4; k++) r[i * 4 + j] += A[i * 4 + k] * B[k * 4 + j];
  return r;
}

function expectMatricesClose(actual: Matrix16, expected: Matrix16, label: string) {
  // 1e-6 is well below the bug's signature (~0.3 sign-flip on matrix entries)
  // and above the float precision floor for these compositions (~1e-15).
  const TOL = 1e-6;
  for (let i = 0; i < 16; i++) {
    const diff = Math.abs(actual[i] - expected[i]);
    expect(
      diff,
      `${label} matrix[${i}] differs by ${diff} (actual=${actual[i]} expected=${expected[i]})`
    ).toBeLessThan(TOL);
  }
}

async function readBothTransforms(
  page: Page,
  rx: string,
  ry: string,
  hov: string
): Promise<{ front: Matrix16; back: Matrix16 }> {
  const raw = await page.evaluate(
    ({ rx, ry, hov }) => {
      const flipCard = document.querySelector(".flip-card") as HTMLElement;
      const front = document.querySelector(".card-front") as HTMLElement;
      const back = document.querySelector(".card-back") as HTMLElement;
      // The faces have `transition: transform .08s linear`, so a fresh
      // var change reads the FROM-state (identity) at t=0 of the transition.
      // Disable the transition for this read so getComputedStyle returns
      // the steady-state matrix.
      front.style.transition = "none";
      back.style.transition = "none";
      // The iridescent controller only writes these vars from mousemove/leave
      // handlers, which we never trigger in this test — so direct sets stick.
      flipCard.style.setProperty("--rx", rx);
      flipCard.style.setProperty("--ry", ry);
      flipCard.style.setProperty("--hov", hov);
      // Force a style recalc before reading.
      void front.offsetWidth;
      void back.offsetWidth;
      return {
        front: getComputedStyle(front).transform,
        back: getComputedStyle(back).transform,
      };
    },
    { rx, ry, hov }
  );
  return { front: parseTransform(raw.front), back: parseTransform(raw.back) };
}

// Three positions cover both --rx and --ry, both signs, and a diagonal that
// exercises non-commutativity of the rotations.
const POSITIONS = [
  { rx: "0deg",    ry: "8.4deg",  label: "right" },
  { rx: "0deg",    ry: "-8.4deg", label: "left" },
  { rx: "4.2deg",  ry: "8.4deg",  label: "upper-right (diagonal)" },
];

const SKUS = discoverIridescentSkus();

if (SKUS.length === 0) {
  test("flip-symmetry has no iridescent cards to check", () => {
    test.skip();
  });
} else {
  for (const sku of SKUS) {
    test(`${sku} hover-tilt is symmetric across flip`, async ({ page }) => {
      await page.goto(`/${sku}/`, { waitUntil: "domcontentloaded" });
      await expect(page.locator(".flip-card")).toBeVisible();

      for (const pos of POSITIONS) {
        const { front, back } = await readBothTransforms(page, pos.rx, pos.ry, "1");
        // When .flip-card.flipped is applied, the parent contributes
        // rotateY(180). The effective screen-space transform of the back
        // face is parent × cardBack — which should equal cardFront.
        const effectiveBack = multiply(ROTATE_Y_180, back);
        expectMatricesClose(effectiveBack, front, `${sku} @ ${pos.label}`);
      }
    });
  }
}
