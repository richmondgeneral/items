# Session Summary — 2026-05-13

Iridescent card design exploration, aged paper wall, V2 generalization
validation, audit + cleanup, policy lock-in. Four PRs merged to `main`
plus three commits in the brand repo and one in plugins.

## 1) Iridescent card design exploration (TVM-196, TVM-197)

- Pulled the Anthropic Claude Design "Iridescent Card" bundle
  (`api.anthropic.com/v1/design/h/uCCMJday5EPAHh7hnHKDwg`).
- Decomposed into six effects: 3D pointer-tilt, iridescent foil
  (radial + diffraction), secondary conic foil, specular spotlight,
  outer glow halo, edge sheen, film grain.
- Reframed the design choice as **texture** (paper-feel, universal-safe)
  vs **theatrics** (foil + halo, scarce on purpose) — "always paper,
  sometimes foil."
- Built a standalone working prototype at
  `~/workspace/experimental/iridescent-card/index.html` for design-chat
  use (not versioned).

## 2) Wall brainstorm: cream → aged paper

- Created a 5-wall comparison (cream, bone, aged paper, sage, charcoal)
  via a URL-hash picker in `RG-0007/iridescent-v2.html` on the
  `experiments/iridescent-card` branch.
- Eliminations:
  - **Charcoal** — soft rounded card corners haloed against hard dark wall.
  - **Cream** — card-on-wall tone collision (white card on cream wall).
  - **Sage** — green cast read as "sickly," not "heritage with intention."
  - **Bone** — too gallery; not heritage enough for the RG voice.
- **Selected: aged paper (`#EFE6D2` → `#E3DAC0`)**. Sage preserved as
  `#wall=sage` URL-hash backup for future comparison.
- `brand/BRAND.md` updated with explicit **wall vs paper split**
  (`--rg-wall` is the wall the cards hover on; `--rg-cream` is the
  paper inside the cards). Sage documented as backup palette.
- **PR #9** (commit `66801ff`) shipped the aged paper wall to:
  - `index.html` (gallery)
  - `template/rg-item-card-template.html`
  - All 20 item cards (`RG-0001`..`RG-0020`)
  - Plus the full V2 iridescent treatment on `RG-0001` as the first
    foil card.

## 3) RG-0003 second foil card (V2 generalization)

- Question: does V2 generalize from a flat book cover (`RG-0001`) to
  a 3D wooden product?
- Built `experiments/iridescent-rg-0003` with full V2 on the
  Pressed-Back Oak Swivel Bar Stool (`RG-0003`, sold archive item).
- User-verified across five states: front at rest, front on hover
  (center), front on hover (corner with full tilt), back desktop,
  back mobile 375×812.
- Verdict: foil reads as "gold sheen sitting on wood." Pattern
  generalizes. SOLD treatment stays legible through the effect.
- **PR #10** (commit `99a3c94`) merged the V2 port to main, including
  a cleanup pass:
  - Mobile breakpoints added to `RG-0003`
  - `.item-image` `box-shadow` restored (matches `RG-0001`)
  - Dead `.buy-button` JS handler removed (port artifact)
  - `og:image` extension typo fixed (`hero.jpg` → `hero.jpeg`)
  - Matching TODO + foil-after-sale policy comment added to both
    `RG-0001` and `RG-0003` CSS headers

## 4) Editorial trigger mechanism

- **Chosen:** `data-finish="iridescent"` attribute on `.card-front`.
- Established by `RG-0001` (PR #9), confirmed as the convention on
  `RG-0003` (PR #10). Runtime gate via
  `document.querySelector('.card-front[data-finish="iridescent"]')`
  in the cursor controller — bails if no match.
- The attribute IS both the editorial signal and the JS trigger.
  Single source of truth.
- Rejected: `<body data-tier>` (inconsistent with existing convention),
  per-item file flag (adds build step), Square custom attribute
  (right for tile propagation only, wrong primary), central manifest
  (drift risk).
- Documented in
  `brand/docs/plans/2026-05-13-iridescent-treatment.md`.

## 5) Foil-after-sale policy

- **Chosen (stance C):** foil is set editorially **at intake** and
  **persists through sale**. "This was always a curated rarity,
  regardless of sold status." Museum metaphor — gold leaf isn't
  stripped after deaccession.
- Rejected: foil-added-at-sale (dilution risk as foil count grows),
  foil-removed-at-sale (inconsistent with the existing as-found /
  as-restored slider pattern; loses archive narrative).
- Codified in
  `brand/docs/plans/2026-05-13-iridescent-treatment.md`.

## 6) Dark mode permanently out of scope

- Decision: light-only by design. No system dark-mode follow, no user
  toggle, no dark variant of any surface — current GH Pages, Square
  Online, or future bespoke storefront.
- Charcoal (`--rg-charcoal`) stays in the palette for type, hero
  gradients, and the SKU badge. Never the page wall.
- Codified in `brand/BRAND.md` under "What this brand isn't" (commit
  `7bf73c1`).

## 7) Refactor TODO at the 3rd foil card

- Current state: V2 CSS (~100 lines) and JS controller (~80 lines)
  duplicated verbatim in `RG-0001/index.html` and `RG-0003/index.html`.
- At the **3rd foil card** (rule of three), extract to:
  - `template/iridescent-finish.css`
  - `template/iridescent-controller.js`
  - Include from every card; gate at runtime on
    `data-finish="iridescent"`.
- TODO comment lives inline in both foil cards so future-someone sees
  it where they'll be editing.

## 8) Audit pass + cleanup fixes (PRs #11, #12)

After PR #10, ran a repo-wide audit (custom checks beyond
`audit-items.sh`) and surfaced two drift classes:

- **`og:title` vs `<title>` mismatch** on `RG-0013` + `RG-0014` —
  shorter `og:title` than actual page title; social previews would
  show wrong text. **PR #11** (commit `d599dfd`) aligned both.
- **Mobile breakpoints missing** on 7 of 20 cards (`RG-0002`,
  `RG-0004`, `RG-0005`, `RG-0006`, `RG-0007`, `RG-0009`, `RG-0014`).
  Without `@media (max-width: 600px)`, back-side content would clip on
  phones. **PR #12** (commit `7884e64`) backfilled the canonical
  101-line block (lifted from `RG-0001`) into all 7. All 20 cards now
  have the breakpoint.

Other audit checks all clean across the 20 items:

- `og:url` SKU matches folder name
- Inline `<img src>` matches hero file on disk (RG-0003's `og:image`
  typo was the only outlier; fixed in PR #10)
- `label.json` `sku` matches folder
- All `label.json` files have required fields
- `--rg-wall` variable present on every card
- No unreplaced `{{placeholder}}` text
- JS analytics SKU references match folder
- `aria-label` SKU references match folder

## 9) Cross-repo work

### brand (`richmondgeneral/brand`)

- `1bdeb7d` — added `brand/iridescent-card.html` (the brand-adapted
  prototype, previously untracked), added
  `brand/wall-light-comparison.html`, documented the wall split in
  `BRAND.md`.
- `7bf73c1` — codified "dark mode out of scope" under *What this
  brand isn't*.
- `2461c54` — updated `docs/plans/2026-05-13-iridescent-treatment.md`
  with the trigger-mechanism decision, foil-after-sale policy, and
  3-card extraction TODO.

### plugins (`richmondgeneral/plugins`)

- `67192ca` — `square-online` plugin **v0.5.0**:
  - New skill `storefront-image-cache-bust` — addresses the Weebly
    storefront CDN keying images by Square catalog image ID. Updating
    in place doesn't bust the cache; the skill mints new image IDs
    and repoints the item. Critical pitfall documented (don't pass
    `object_id` on POST `/v2/catalog/images` for replacements).
  - Enhancement to `storefront-hero-tiles` — multi-route support:
    same snippet can render different tile sets on `/s/shop` plus
    `/shop/<slug>/<category_id>` top-level category pages.
  - SPA-idempotent via `#rg-hero[data-rg-route]`; `body.rg-hero-active`
    class hides Square's native subcategory tiles when our hero is on.

## 10) Open follow-ups (NOT done today)

- **TVM-197** Claude Design exploration for the bespoke large-screen
  storefront — still in pure-design state, no work started.
- Square Online tile treatment via Snippets API — open experiment in
  TVM-196's checklist; not started.
- Static-render pipeline for email / social / Whatnot (pre-rendered
  foil PNG) — open experiment in TVM-196's checklist; not started.
- Third foil card → triggers the V2 extraction refactor described in §7.
- Linear MCP server was disconnected during the wrap; final TVM-196
  follow-up comment ("PRs #10, #11, #12 merged + decisions locked")
  not yet posted. To post when MCP is back.

## 11) Housekeeping

- Added `.playwright-cli/` to `items/.gitignore` (local Playwright
  debug artifacts — console logs, page snapshots — shouldn't be
  committed).
- Stale local branch in `skills` repo: `adoring-lamarr` (5 months
  old, `image-processor` consolidation; not on origin). Candidate
  for local cleanup; not deleted this session because the branch
  has commits not necessarily reflected in `main`.
- Stale **remote** branches on `items` worth cleaning up when
  convenient:
  - `claude/analyze-codebase-015QN4Vv9U3JqFQjz1FPhnoe`
  - `claude/refactor-auto-onboarding-TyZdT`
  - `cleanup-stale-scripts`
  - `harden-rg-0007-close-3` — already merged via PR #7 (Feb 14,
    2026); confirmed during the earlier code review.

## 12) PRs merged today

| PR | Commit | Title |
|---:|:---:|:---|
| #9 | `66801ff` | Aged paper wall + RG-0001 V2 (merged via `experiments/iridescent-card`) |
| #10 | `99a3c94` | RG-0003 V2 iridescent finish + cleanup + policy lock |
| #11 | `d599dfd` | Align og:title to `<title>` on RG-0013 + RG-0014 |
| #12 | `7884e64` | Mobile breakpoint backfill on 7 stragglers |

All branches deleted from origin after merge.
