# Design: Canonical "Tap for Story" flip affordance for item cards

- **Date:** 2026-06-20
- **Status:** Approved (brainstorming) → ready for implementation plan
- **Repo:** `richmondgeneral/items` (GitHub Pages)

## Problem

Observed: RG-0014 shows a prominent "Tap for details" callout while "most other cards
don't." Investigation found the opposite of that first read:

- **All 50 item pages already carry a flip hint** (`.flip-hint`). None are missing it.
- **RG-0014 is the lone placement outlier:** an old-template floating white *pill* over
  the hero image (`position:absolute; bottom/right; rounded; bold; drop-shadow`). Every
  other card uses a subtle gray inline hint (`font-size:0.75rem; color:#888`) in the
  front-footer next to the price — so faint it reads as absent. That visual gap is why
  RG-0014 looked like the one "with" a callout.
- **Wording has drifted three ways:** "Tap for story" (×48 + template), "Tap for details"
  (RG-0014), "Tap to learn more" (RG-0007).
- **Print is already solved:** the template and every card hide `.flip-hint` in
  `@media print { .flip-hint { display:none } }`. The hint never prints.
- **No deliberate "remove the callout" decision was made.** RG-0014 and RG-0007 are early
  items that predate the template settling on the inline hint and were never retrofitted.

## Decision

Governing principle — **two surfaces, two jobs:**

| Surface | Interaction | Affordance | Change |
|---|---|---|---|
| Gallery grid (`index.html`) | navigates to the item page | `View Story →` | **none** |
| Single item page (`RG-XXXX/`) | flips (a non-obvious gesture) | `Tap for Story` chip + one-time nudge | **this work** |
| Print | n/a | hidden | **none** (already hidden) |

Discoverability only matters on the single item page: flipping is a non-standard gesture,
and the page is a sparse one-card canvas where a defined hint costs little cognitive load.
The gallery is dense navigation, where subtlety is correct. Desktop stays calm (the chip is
*clearer, not louder*); mobile reads a touch more present, which is where the gesture lives.

### Affordance (item page only) — Approach C

Replace the bare gray `.flip-hint` text with a calm, *defined* chip in the front-footer
(no floating pill over the hero image). CSS-only — no JavaScript.

```css
.flip-hint {
  display: inline-flex; align-items: center; gap: 0.3rem;
  font-size: 0.72rem; font-weight: 600;
  color: var(--rg-brown);
  background: var(--rg-cream);               /* calm; distinct from the gold price */
  border: 1px solid rgba(107, 68, 35, 0.18);
  padding: 0.25rem 0.6rem; border-radius: 999px; line-height: 1;
}

@media (prefers-reduced-motion: no-preference) {
  .flip-icon { animation: flip-nudge 1.4s ease 0.9s 2; transform-origin: center; }
  @keyframes flip-nudge { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.18); } }
}
```

- The nudge is a **two-pulse scale of the flip icon** ~0.9s after load, then rest — catches
  a first-timer's eye, then goes quiet.
- `prefers-reduced-motion: reduce` users get the static chip, no animation.
- Final fill/tint confirmed against a screenshot in the QA pass: must stay distinct from the
  gold price and read calm on desktop.

### Wording

`Tap for Story` (title case) on every item page. Retires all three current variants.

### Rollout scope

- `template/rg-item-card-template.html` — the canonical source (update first).
- All 50 item pages:
  - **48** are a CSS-class + text swap (and the title-case wording).
  - **RG-0014** (now sold) and **RG-0007** use the *old* template structure (hint is a pill
    over the image; no `front-footer`). Their hint must be **relocated** to the front-footer
    and restyled, not just text-swapped.

### Living-test carve-out (→ SOP)

Items running live experiments keep their **functionality** untouched; only **styles** are
standardized:

- **RG-0001** — touch/motion ("TILT") experiment.
- **RG-0011** — As-Found / AI-restored drag-to-compare image slider
  (`variant-stack`, `data-mode="slider"`, `data-variant="as-found|as-restored"`).

Both still receive the `Tap for Story` chip (a style update, explicitly allowed), but their
experimental markup/JS is **not** altered. This rule is added to `items/CLAUDE.md` as a
standing **"Living-test items"** policy, alongside the canonical-affordance spec, so future
site-wide style sweeps don't clobber experiments.

## Verification

- `./validate-item.sh RG-XXXX` for each touched item.
- Playwright screenshot harness (`npm run ui:review`) on desktop + mobile, front + back:
  confirm the chip renders, the nudge fires once (and *not* under reduced-motion), the
  gallery is unchanged, and the RG-0001 / RG-0011 experiments still function.

## Out of scope / YAGNI

- No change to gallery tiles or to print CSS.
- No new build step; pure HTML/CSS, nudge is CSS-only (no JS).
- Not deleting the now-dead `.buy-button` / `.qr-section` CSS left on sold items — that's a
  separate cleanup pass, not part of this work.
