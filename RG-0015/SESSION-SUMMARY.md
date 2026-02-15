# RG-0015 Onboarding & Workflow Evolution — Session Summary

**Date:** February 14–15, 2026
**Item:** Dick Tracy: The Art of Chester Gould (1978) Exhibition Catalogue
**SKU:** RG-0015

---

## What Was Accomplished

### RG-0015: Fully Onboarded Across All Channels

RG-0015 is now live on both Square and Whatnot. Every phase of the rg-full-auto workflow was completed for this item:

**Square Catalog (Phases 2–6):**
- Catalog Item ID: `N6UKEMUCS6V2VDVBL4BXSYEV`
- Variation ID: `TFNLYCOLXOIE4DWPLEXI7LFU`
- Hero Image ID: `XXPWGV3PEX6VYRPTN564GGYH`
- Payment Link: https://square.link/u/OouZZes0
- 6 detail photos (IMG_0077 through IMG_0082) background-removed and uploaded to Square

**Whatnot Marketplace (Phase 8):**
- Listing created via Chrome automation and saved as Active
- Category: Rare & Vintage Books
- Price: $40 | Condition: Good | Binding: Softcover
- Publication Period: 1950–1999 | Topic: Art History & Criticism

**GitHub Pages (Phase 7):**
- `index.html` info card published
- Hero image live at `https://richmondgeneral.github.io/items/RG-0015/hero.png`
- 6 detail images live at `https://richmondgeneral.github.io/items/RG-0015/IMG_007X-nobg.png`
- QR code generated

### RG-0015 File Inventory

```
RG-0015/
├── hero.png                 (5 MB — primary product photo)
├── IMG_0077.jpg … IMG_0082.jpg   (6 original detail photos)
├── IMG_0077-nobg.png … IMG_0082-nobg.png  (6 background-removed)
├── index.html               (info card for GitHub Pages)
└── qr-code.png              (links to info card)
```

---

## New Capabilities Delivered

### 1. Batch Background Removal — `process_group.py`

**Location:** `~/.claude/skills/image-processor/scripts/process_group.py`
**Author:** Codex agent (commit `b15c551` in skills repo)

Processes all eligible images in an item directory through the existing image-processor routing/fallback logic. Supports glob-style `--include` patterns and `--quality premium` for remove.bg.

```bash
uv run --project ~/.claude/skills python \
  ~/.claude/skills/image-processor/scripts/process_group.py \
  --input-dir ~/workspace/square/items/RG-XXXX \
  --include "IMG_*.jpg" \
  --quality premium --model auto --json
```

**Live test:** Ran on RG-0015 — processed 6 detail photos (IMG_0077–IMG_0082) to `-nobg.png` outputs.

### 2. Bulk Square Image Upload — `upload_batch.py`

**Location:** `~/.claude/skills/square-image-upload/scripts/upload_batch.py`
**Author:** Codex agent (commit `b15c551` in skills repo)

Uploads all matching image files in a directory to a Square catalog item. The `--no-auto-primary` flag is critical — it prevents detail photo uploads from overriding the hero image that was already set as primary.

```bash
uv run --project ~/.claude/skills python \
  ~/.claude/skills/square-image-upload/scripts/upload_batch.py \
  --directory ~/workspace/square/items/RG-XXXX \
  --item-id <CATALOG_ITEM_ID> \
  --include "*-nobg.png" \
  --no-auto-primary --json
```

**Live test:** Uploaded 6 detail photos to RG-0015's Square catalog item (`N6UKEMUCS6V2VDVBL4BXSYEV`).

### 3. Whatnot CSV Bulk Import Workflow — Phase 8

**What changed:** Phase 8 of rg-full-auto was rewritten from a Chrome automation approach to a CSV bulk import approach.

**Why:** Chrome automation for Whatnot forms was slow, fragile, and couldn't handle image uploads reliably. The CSV import approach uses publicly hosted GitHub Pages image URLs, eliminating file upload automation entirely.

**How it works:**
1. After completing Phases 0–7 (and git push), append a row to the batch CSV file at `~/workspace/square/items/rg-inventory/whatnot-import.csv`
2. Upload the CSV to Whatnot at `whatnot.com/dashboard/inventory` → Import CSV
3. Whatnot fetches the hero image from GitHub Pages automatically

**Image URL pattern:** `https://richmondgeneral.github.io/items/RG-XXXX/hero.png`

**CSV schema (18 columns):**
```
Category, Sub Category, Title, Description, Quantity, Type, Price,
Shipping Profile, Offerable, Hazmat, Condition, Cost Per Item, SKU,
Image URL 1, Image URL 2, Image URL 3, Image URL 4, Image URL 5,
Image URL 6, Image URL 7, Image URL 8
```

**Batch file created** with RG-0015 as the first entry. Future items just need one `echo >>` command to append a row, then a single CSV upload imports everything at once.

---

## Workflow State: rg-full-auto v2.8

The skill is now a 9-phase workflow (Phases 0–8), though the frontmatter still says "8-phase" and version `2.8`. The phases are:

| Phase | Name | Status |
|-------|------|--------|
| 0 | Photo Intake & Background Removal | ✅ Now with `process_group.py` batch mode |
| 1 | Appraisal & Lot Tracking | ✅ Delegates to rg-lot-tracker |
| 2 | Square Catalog Creation | ✅ |
| 3 | Hero Image Upload | ✅ |
| 4 | Payment Link | ✅ |
| 5 | Label Generation | ✅ |
| 6 | Detail Image Upload | ✅ Now with `upload_batch.py --no-auto-primary` |
| 7 | Info Card & GitHub Pages | ✅ |
| 8 | Whatnot CSV Import | ✅ NEW — CSV bulk approach |

---

## Key Decisions & Lessons Learned

**Chrome `computer` tool vs `javascript_tool`/`form_input`:** For filling web forms, `form_input` with element refs from `find`/`read_page` is faster and more reliable than coordinate-based click/type. The `computer` tool should be reserved for visual tasks like screenshots and scrolling.

**CSV import beats Chrome automation for Whatnot:** The image upload problem was the fundamental blocker. GitHub Pages as an image CDN + CSV import was the elegant solution — no file dialogs, no DataTransfer API hacks, no browser extensions needed.

**`--no-auto-primary` flag matters:** When uploading detail photos in bulk, the first image would otherwise become primary and override the hero image. This flag prevents that.

---

## Pending Items

- **Version bump to v2.9:** The SKILL.md frontmatter still says v2.8 and "8-phase" — should be updated to v2.9 / 9-phase with a changelog entry for the Whatnot phase and batch image processing integration.
- **Whatnot CSV import not yet tested end-to-end:** RG-0015 was listed via Chrome automation. The CSV import flow has not been validated with an actual upload to Whatnot yet.
- **Detail image URLs in Whatnot CSV:** The whatnot-import.csv for RG-0015 only includes `Image URL 1` (hero). Could be updated to include the 6 detail photos in Image URL 2–7 now that they're live on GitHub Pages.
- **ITEM_CARD.md missing:** The RG-0015 directory has `index.html` but no `ITEM_CARD.md` reference file.

---

## Commits

| Repo | Commit | What |
|------|--------|------|
| skills | `b15c551` | Batch bg removal (`process_group.py`), bulk upload (`upload_batch.py`), `--no-auto-primary`, updated skill docs, 27 tests passing |
| items | `c6abf41` | RG-0015 detail photos (6× `-nobg.png`) |
