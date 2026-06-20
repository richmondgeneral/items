# "Tap for Story" Flip Affordance — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Standardize the single-item-page flip hint to a calm, defined "Tap for Story" chip with a reduced-motion-safe one-time icon nudge, across the template + all 50 item pages, without touching the gallery, print behavior, or living-test functionality.

**Architecture:** Pure HTML/CSS, no build step. CSS is inlined per item page, so the chip rule must be updated in every file plus the template. 49 pages share one of 4 near-identical inline `.flip-hint` rules → updated by a regex script. RG-0014 (sold, old "pill over image" structure) is updated by hand. Living-test items (RG-0001 TILT, RG-0011 image slider) get only the style/wording change; their JS is untouched.

**Tech Stack:** Vanilla HTML/CSS, Python 3 (rollout + verifier scripts, stdlib only), `validate-item.sh`, Playwright (`npm run ui:review`).

**Design doc:** `docs/plans/2026-06-20-tap-affordance-design.md`

---

## Execution hazards (read before starting)

- **Concurrent writers share this checkout.** At plan time, another session had uncommitted edits to `index.html` and `RG-0027/index.html` (in-flight RG-0027 work). **Execute in a fresh worktree off the latest `origin/main`** (`git worktree add ../items-tapfix origin/main`) so you never touch their working tree. If `RG-0027/index.html` still has uncommitted edits elsewhere when you merge, apply the RG-0027 chip change **last** and rebase, or coordinate so that work lands first.
- **Stage explicit paths only — never `git add -A`.** Other items' work sits alongside.
- **Re-verify branch + `git fetch` 0-behind immediately before every commit/push** (clean fast-forward, never `--force`).
- **Do not touch `index.html` (gallery) or any `@media print` block.** Out of scope by design.

---

## Task 1: Update the template (canonical source)

**Files:**
- Modify: `template/rg-item-card-template.html` (the `.flip-hint` CSS rule, add `@keyframes`, and the hint text)

**Step 1 — Replace the `.flip-hint` CSS rule.** Find:
```css
        .flip-hint {
            font-size: 0.75rem;
            color: #888;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            line-height: 1;
        }
```
Replace with the chip + reduced-motion nudge:
```css
        .flip-hint {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--rg-brown);
            background: var(--rg-cream);
            border: 1px solid rgba(107, 68, 35, 0.18);
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            line-height: 1;
        }

        @media (prefers-reduced-motion: no-preference) {
            .flip-icon { animation: flip-nudge 1.4s ease 0.9s 2; transform-origin: center; }
            @keyframes flip-nudge { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.18); } }
        }
```

**Step 2 — Fix the wording.** In the template's front-footer markup, change `Tap for story` → `Tap for Story`.

**Step 3 — Verify (grep assertions).**
```bash
grep -q 'border-radius: 999px' template/rg-item-card-template.html && \
grep -q 'flip-nudge' template/rg-item-card-template.html && \
grep -q 'Tap for Story' template/rg-item-card-template.html && \
! grep -q 'Tap for story' template/rg-item-card-template.html && echo "TEMPLATE OK"
```
Expected: `TEMPLATE OK`

**Step 4 — Visual check.** Copy the template to a scratch file, replace `{{...}}` placeholders or open directly, screenshot front side; confirm a calm cream/brown chip by the price and the icon pulses twice on load (and not under OS "reduce motion").

**Step 5 — Commit.**
```bash
git add template/rg-item-card-template.html
git commit -m "feat(template): 'Tap for Story' flip-hint chip + reduced-motion nudge"
```

---

## Task 2: Write the verifier (test-first)

**Files:**
- Create: `scripts/ui/verify_flip_hint.py`

**Step 1 — Write the verifier.** It enforces the invariants on every `RG-*/index.html`:
```python
#!/usr/bin/env python3
"""Verify the canonical 'Tap for Story' flip-hint chip across all item pages."""
import re, sys, glob

BAD_WORDING = ("Tap for story", "Tap for details", "Tap to learn more")
fails = []
for f in sorted(glob.glob("RG-*/index.html")):
    html = open(f, encoding="utf-8").read()
    # 1) exactly one .flip-hint rule, and it is the chip (has border-radius: 999px)
    m = re.search(r"\.flip-hint\s*\{[^}]*\}", html)
    if not m or "border-radius: 999px" not in m.group(0):
        fails.append(f"{f}: .flip-hint is not the chip rule")
    # 2) reduced-motion nudge present
    if "flip-nudge" not in html or "prefers-reduced-motion" not in html:
        fails.append(f"{f}: missing reduced-motion flip-nudge")
    # 3) canonical wording, no stale variants
    if "Tap for Story" not in html:
        fails.append(f"{f}: missing 'Tap for Story'")
    for bad in BAD_WORDING:
        if bad in html:
            fails.append(f"{f}: still contains '{bad}'")
    # 4) print still hides the hint (must NOT be removed)
    if not re.search(r"@media print[\s\S]*?\.flip-hint[\s\S]*?display\s*:\s*none", html):
        fails.append(f"{f}: print no longer hides .flip-hint")

print("\n".join(fails) if fails else "ALL ITEM PAGES OK")
sys.exit(1 if fails else 0)
```

**Step 2 — Run it (expect failure).**
```bash
python3 scripts/ui/verify_flip_hint.py
```
Expected: many `... is not the chip rule` / `missing 'Tap for Story'` lines, exit 1. (This confirms the verifier detects the pre-change state.)

**Step 3 — Commit.**
```bash
git add scripts/ui/verify_flip_hint.py
git commit -m "test(ui): verifier for canonical Tap for Story flip-hint"
```

---

## Task 3: Roll out to the 49 inline-style pages (script)

**Files:**
- Create: `scripts/ui/rollout_flip_hint.py`
- Modify: all `RG-*/index.html` **except `RG-0014`** (49 files)

**Step 1 — Write the rollout script.** Handles all 4 inline `.flip-hint` variants; skips RG-0014; idempotent; fails loudly per file.
```python
#!/usr/bin/env python3
"""Roll the canonical 'Tap for Story' chip into the 49 inline-style item pages."""
import re, glob, sys

CHIP = """.flip-hint {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--rg-brown);
            background: var(--rg-cream);
            border: 1px solid rgba(107, 68, 35, 0.18);
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            line-height: 1;
        }

        @media (prefers-reduced-motion: no-preference) {
            .flip-icon { animation: flip-nudge 1.4s ease 0.9s 2; transform-origin: center; }
            @keyframes flip-nudge { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.18); } }
        }"""

changed, errors = [], []
for f in sorted(glob.glob("RG-*/index.html")):
    if f.startswith("RG-0014"):   # old structure, handled by hand in Task 4
        continue
    html = open(f, encoding="utf-8").read()
    orig = html
    # replace the (single) inline .flip-hint rule; guard against the pill variant
    m = re.search(r"\.flip-hint\s*\{[^}]*\}", html)
    if not m:
        errors.append(f"{f}: no .flip-hint rule found"); continue
    if "position: absolute" in m.group(0):
        errors.append(f"{f}: unexpected pill-style .flip-hint (skipped)"); continue
    if "flip-nudge" not in html:            # idempotency: only insert once
        html = html[:m.start()] + CHIP + html[m.end():]
    # wording → title case
    html = html.replace("Tap for story", "Tap for Story").replace("Tap to learn more", "Tap for Story")
    if html != orig:
        open(f, "w", encoding="utf-8").write(html); changed.append(f)

print(f"changed {len(changed)} files")
if errors:
    print("ERRORS:\n" + "\n".join(errors)); sys.exit(1)
```

**Step 2 — Run it.**
```bash
python3 scripts/ui/rollout_flip_hint.py
```
Expected: `changed 49 files`, no ERRORS. (RG-0014 skipped; RG-0007's "Tap to learn more" handled by the wording replace.)

**Step 3 — Run the verifier (RG-0014 will still fail — that's expected).**
```bash
python3 scripts/ui/verify_flip_hint.py | grep -v 'RG-0014' | head
```
Expected: no non-RG-0014 failures.

**Step 4 — Commit (explicit paths; do NOT `git add -A`).**
```bash
git add scripts/ui/rollout_flip_hint.py $(git diff --name-only 'RG-*/index.html')
git commit -m "feat(items): roll Tap for Story chip into 49 item pages"
```

---

## Task 4: RG-0014 by hand (sold, old "pill" structure)

**Files:**
- Modify: `RG-0014/index.html`

RG-0014 has no `front-footer`; its sold front-info is `<h1>` + `<p class="item-era">` + `<p class="item-price sold-price">Sold · $20.00</p>`, and its hint is a `.flip-hint` **pill positioned over the image** reading "Tap for details".

**Step 1 — Remove the pill markup** from inside `.item-image-container` (the `<div class="flip-hint">…Tap for details…</div>` block, lines ~442–450).

**Step 2 — Add a front-footer** in `.front-info`, wrapping the existing sold price with the chip hint, mirroring the standard structure:
```html
                <div class="front-info">
                    <h1 class="item-title">1969 Chicago Cubs "Cub Power" LP Record</h1>
                    <p class="item-era">1969 • Quill Records • Verified Playable</p>
                    <div class="front-footer">
                        <span class="item-price sold-price">Sold · $20.00</span>
                        <span class="flip-hint">
                            <svg class="flip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/>
                                <path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>
                            </svg>
                            Tap for Story
                        </span>
                    </div>
                </div>
```
(Drop the old standalone `<p class="item-price sold-price">`.)

**Step 3 — Replace RG-0014's pill `.flip-hint` CSS** (the `position: absolute … box-shadow` rule) with the chip rule + reduced-motion block from Task 1. Add `.front-footer { display: flex; justify-content: space-between; align-items: center; }` if not present. Add a `.flip-icon { width: 14px; height: 14px; }` rule if RG-0014 lacks one (it had no `.flip-icon`).

**Step 4 — Verify.**
```bash
python3 scripts/ui/verify_flip_hint.py        # expect: ALL ITEM PAGES OK
./validate-item.sh RG-0014                     # expect: Validation passed
```

**Step 5 — Commit.**
```bash
git add RG-0014/index.html
git commit -m "feat(RG-0014): relocate flip hint to front-footer chip (old structure)"
```

---

## Task 5: Confirm living-test items still work (RG-0001, RG-0011)

**Files:** none changed here (verification only — the chip already applied via Task 3).

**Step 1 — RG-0001 (TILT touch/motion).** Open `RG-0001/index.html`; confirm the chip rendered and the `TILT`/motion JS block is byte-identical to pre-change (`git diff RG-0001/index.html` should show **only** the `.flip-hint` rule, the inserted keyframes, and the wording — nothing in the tilt script). Load the page; confirm tilt still responds to cursor/motion.

**Step 2 — RG-0011 (As-Found/AI-restored slider).** Same diff check (only flip-hint/wording lines). Load the page; confirm the `variant-stack` drag-to-compare slider still drags and the keyboard handle works.

**Step 3 — If either diff shows unexpected changes,** revert that file and apply the chip + wording by hand, leaving the experiment markup/JS untouched. No commit if clean (already committed in Task 3); otherwise commit the hand-fix.

---

## Task 6: Codify the policy in `items/CLAUDE.md`

**Files:**
- Modify: `items/CLAUDE.md`

**Step 1 — Fix the stale line.** Under "Item Card Features → Front Side", change `"Tap to learn more" hint` → `"Tap for Story" hint (chip; hidden in print)`.

**Step 2 — Add a "Canonical flip affordance" note** under "Item Card Features":
> **Flip affordance (canonical).** Single item pages show one flip hint: a calm chip in the front-footer — flip icon + **"Tap for Story"** (title case) — with a one-time `.flip-icon` nudge gated by `prefers-reduced-motion`. It is hidden in `@media print`. The gallery grid uses `View Story →` instead (navigation, not flip). Spec + rationale: `docs/plans/2026-06-20-tap-affordance-design.md`.

**Step 3 — Add a "Living-test items" rule** (new short section):
> ## Living-test items
> Some items run live experiments. **Do not change their functionality during site-wide sweeps — update styles only.** Known living tests: **RG-0001** (touch/motion "TILT"), **RG-0011** (As-Found/AI-restored drag-to-compare slider, `variant-stack`/`data-mode`). They receive standard style/wording updates (e.g., the flip-hint chip) but their experimental markup/JS must be preserved. When in doubt, `git diff` the file and confirm only style/text lines changed.

**Step 4 — Commit.**
```bash
git add items/CLAUDE.md   # path is CLAUDE.md from inside items/
git commit -m "docs(items): canonical flip affordance + living-test items policy"
```

---

## Task 7: Full verification

**Step 1 — All item pages pass the invariants.**
```bash
python3 scripts/ui/verify_flip_hint.py        # expect: ALL ITEM PAGES OK
```

**Step 2 — Per-item validator (no regressions).**
```bash
for d in RG-*; do [ -d "$d" ] && ./validate-item.sh "$d" >/dev/null || echo "FAIL $d"; done; echo done
```
Expected: only `done` (no `FAIL` lines).

**Step 3 — Playwright screenshot QA.**
```bash
npm run ui:review
```
Review desktop + mobile, front + back: chip renders calm and distinct from the gold price; gallery tiles unchanged; spot-check the icon nudge fires once then rests; set OS "Reduce Motion" and confirm no animation; confirm RG-0001 tilt + RG-0011 slider still function.

**Step 4 — Gallery + print untouched (guard).**
```bash
git diff --name-only origin/main | grep -E '(^|/)index\.html$' && echo "WARN gallery touched" || echo "gallery clean"
```
Expected: `gallery clean`.

---

## Task 8: Push

**Step 1 — Re-verify and push (clean fast-forward).**
```bash
git fetch origin main -q
[ "$(git rev-list --count HEAD..origin/main)" = "0" ] || { echo "behind — rebase first"; exit 1; }
git push origin main
```
GitHub Pages auto-deploys in 1–2 min.

---

## Out of scope / YAGNI
- No gallery (`index.html`) or `@media print` changes.
- No deletion of dead `.buy-button`/`.qr-section` CSS on sold items (separate cleanup).
- No new build step; nudge is CSS-only.
