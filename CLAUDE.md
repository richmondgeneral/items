# CLAUDE.md

This file provides guidance to AI agents (Claude, Warp, etc.) when working with code in this repository.

## Repository Overview

This is a **GitHub Pages site** for Richmond General, showcasing a curated vintage and antique collection with museum-style info cards. Each item gets a dedicated page with flip-card UI, story/provenance, and integrated Square payment links.

**Live Site:** [richmondgeneral.github.io/items](https://richmondgeneral.github.io/items/)  
**Repository:** `git@github.com:richmondgeneral/items.git`  
**Skills Repository:** [github.com/richmondgeneral/skills](https://github.com/richmondgeneral/skills)

### Purpose & Scope

This repository is the source of truth for:
- GitHub Pages item cards (`RG-XXXX/index.html`)
- Item media used by the site (`hero.*`, `qr-code.png`)
- Item-level label metadata (`RG-XXXX/label.json`)

**Out of scope:**
- Skill definitions (maintained in `richmondgeneral/skills`)
- Reusable skill automation logic

## Architecture

### Site Structure

```
items/
├── index.html                    # Gallery landing page
├── 404.html                      # Custom 404 "Treasure Not Found" page
├── readme.md                     # User-facing quick start
├── CLAUDE.md                     # This file (agent guide)
├── SKILLS.md                     # Skills migration pointer
├── assets/
│   ├── favicon.svg               # RG favicon
│   └── working-images/           # Original images before processing
├── template/
│   └── rg-item-card-template.html  # Master template for new items
├── scripts/
│   ├── labels/build_batch_csv.py   # Batch label CSV builder
│   └── ui/                         # UI screenshot QA tooling
├── rg-inventory/                 # Inventory management files
│   ├── rg-inventory-tracker.xlsx
│   ├── rg-labels-batch.csv
│   └── rg-labels-batch.xlsx
├── RG-0001/                      # Item folders
│   ├── index.html                # Item card page
│   ├── hero.jpeg                 # Processed item image
│   ├── label.json                # Label metadata source
│   └── qr-code.png               # Square payment QR code
└── RG-XXXX/                      # Pattern for all items
```

### Technology Stack

- **Framework**: Pure HTML/CSS/JavaScript (no build step)
- **Hosting**: GitHub Pages (automatic deployment from `main` branch)
- **Fonts**: Google Fonts (Playfair Display, Source Sans Pro)
- **Styling**: Vanilla CSS with CSS Variables
- **Interactive Elements**: Pure JavaScript for flip card animation

### Design System

**Brand Colors:**
```css
--rg-gold: #C9A961
--rg-cream: #F5F1E8
--rg-charcoal: #2C2C2C
--rg-brown: #6B4423
```

**Typography:**
- Headings: Playfair Display (serif)
- Body: Source Sans Pro (sans-serif)

## Item Folder Structure

### Required Files

Every item folder (`RG-XXXX/`) **MUST** contain:

```
RG-XXXX/
├── index.html         # Item card page (from template)
├── hero.{jpeg|png}    # Primary item image (processed, background removed)
├── label.json         # Label metadata source for batch export
└── qr-code.png        # Square payment QR code (PNG format only)
```

**File requirements:**
- **index.html**: Generated from `template/rg-item-card-template.html` with all `{{placeholders}}` replaced
- **hero.{jpeg|png}**: Processed image (background removed, optimized for web, < 1MB recommended)
- **label.json**: Required fields: `sku`, `product_name`, `attributes`, `price`, `condition`, `condition_notes`, `qr_code_url`
- **qr-code.png**: QR code linking to Square payment page (PNG format, NOT SVG)

### Optional Files

Item folders MAY contain additional images:

```
RG-XXXX/
├── detail.{jpeg|png}  # Close-up or alternate view
├── mark.png           # Maker's mark, signature, or stamp
├── label.png          # Original labels, tags, or certificates
└── [custom].{jpeg|png} # Other specific images (e.g., titlepage.jpeg)
```

### Naming Conventions

- **Item folders**: `RG-XXXX` (zero-padded 4-digit number, e.g., `RG-0001`, `RG-0042`)
- **Images in item folders**: `hero.{jpeg|png}`, `qr-code.png`, `detail.{jpeg|png}`, `mark.png`, `label.png`
- **Custom images**: Use descriptive lowercase names with hyphens (e.g., `title-page.jpeg`)
- **Working images**: `RG-XXXX-[type].{jpeg|png}` in `assets/working-images/`

## Image Management

### Working Images Directory

**Path**: `assets/working-images/`

This directory stores original/source images before processing:
- Original photos (with backgrounds)
- Detail shots and close-ups
- Maker's marks and labels
- Work-in-progress files

### Image Processing Workflow

**1. Add original image:**
```bash
cp ~/Desktop/photo.jpeg assets/working-images/RG-XXXX-hero.jpeg
```

**2. Process with image-processor skill:**
- Removes background (via Nano Banana Pro, Gemini 2.5, or remove.bg)
- Creates `*-converted.*` file in root (git-ignored)
- Uploads to Square catalog
- Optimizes for web

**3. Deploy to item folder:**
```bash
cp RG-XXXX-hero-converted.jpeg RG-XXXX/hero.jpeg
```

### What's Tracked in Git

**Tracked** (version controlled):
- `assets/working-images/*` - Original source images
- `RG-XXXX/hero.{jpeg|png}` - Final deployed images
- `RG-XXXX/qr-code.png` - Payment QR codes

**Ignored** (`.gitignore`):
- `*-converted.*` - Processed images (temporary)
- `*.zip` - Archive files
- Root-level working files

## Adding New Items

### Automated Workflow (Recommended)

**When you have a photo of an item**, use the `rg-full-auto` skill workflow:

1. **Load photo into Claude Desktop**
   - AirDrop from iPhone to Mac
   - Drag/drop or attach image to Claude

2. **Say "new item"** or "add to inventory"
   - Claude loads item-processing skills from `richmondgeneral/skills`
   - Claude analyzes the photo visually
   - Claude asks for your approval at key steps

3. **Claude handles everything**:
   - Phase 1: Appraisal & research (visual analysis, pricing)
   - Phase 2: Background removal (remove.bg API)
   - Phase 3: Square catalog creation (with categories, tax, SEO)
   - Phase 4: Image upload to Square
   - Phase 5: Payment link generation
   - Phase 6: Label metadata generation (`RG-XXXX/label.json`)
   - Phase 7: GitHub Pages deployment (optional)

4. **You supervise**:
   - Approve pricing after Phase 1
   - Approve catalog creation after Phase 3
   - Approve publishing after Phase 7

**Output:** Complete item listing with:
- Square catalog item ID
- Payment link (square.link/u/XXXXXXXX)
- Item-level `label.json` metadata
- GitHub Pages card (optional)
- Files organized in `RG-XXXX/` folder

**Requirements:**
- `SQUARE_ACCESS_TOKEN` set in environment
- `REMOVEBG_API_KEY` set in environment (get at remove.bg/api)

### Manual Workflow (Alternative)

If not using the automated skill:

1. Create folder: `mkdir RG-XXXX`
2. Copy template: `cp template/rg-item-card-template.html RG-XXXX/index.html`
3. Manually replace all {{placeholders}} (see template header for full list)
4. Add images following the structure above
5. Run `./validate-item.sh RG-XXXX` before deploying
6. Deploy:
   ```bash
   git add RG-XXXX
   git commit -m "Add RG-XXXX: [Item Name]"
   git push origin main
   ```

## Validation & Testing

### Pre-Deployment Validation

**Single item check:**
```bash
./validate-item.sh RG-XXXX
```

**Checks performed:**
- ✓ Required files exist (index.html, hero.*, qr-code.png)
- ✓ label.json exists and schema validates
- ✓ No unreplaced {{placeholders}}
- ✓ Working images present in assets/working-images/
- ✓ Square payment link present
- ✓ Flip card UI and accessibility features
- ⚠ File sizes (warns if > 1MB)
- ⚠ SVG QR codes (should be PNG only)

**Exit codes:**
- 0: Validation passed (may have warnings)
- 1: Validation failed (errors found)

### Repository-Wide Audit

**Audit all items:**
```bash
./audit-items.sh
```

**Audits:**
- File presence and naming
- Design elements (brand colors, fonts, flip card UI)
- Square integration (payment links, QR codes)
- Accessibility features (ARIA, keyboard nav)
- Print styles

**Validate all items:**
```bash
for d in RG-*; do
  [ -d "$d" ] || continue
  ./validate-item.sh "$d" || true
done
```

### Label Batch Export

Build a printable label CSV from per-item metadata:

```bash
npm run labels:build
```

Default output:
- `qa-artifacts/labels/rg-labels-batch.csv`

### Local Preview

Serve locally and test in browser:

```bash
python3 -m http.server 8000
# Or: npx serve .
```

Then visit:
- `http://localhost:8000/`
- `http://localhost:8000/RG-XXXX/`

### Manual QA Checklist

For each changed item page:
- [ ] Flip interaction works with click/tap and keyboard
- [ ] Front/back content is readable on desktop and mobile widths
- [ ] Buy button points to a real destination (not `#`)
- [ ] Hero image and QR code render correctly
- [ ] Print stylesheet exists and produces usable output

### Playwright Screenshot QA

This repo includes a screenshot-based UI harness for agent review.

**One-time setup:**
```bash
npm install
npm run ui:install-browsers
```

**Capture screenshots + build agent review pack:**
```bash
npm run ui:review
```

This runs:
- `playwright test` against all `RG-*` item pages (desktop + mobile, front + back)
- Basic assertions (flip-card visible, buy link not `#`, no broken images, no horizontal overflow)
- Screenshot capture to `qa-artifacts/screenshots/`
- Review-pack generation in `qa-artifacts/agent-review/`

**Agent review and gating:**
1. Run `npm run ui:review`
2. Give `qa-artifacts/agent-review/review_prompt.md` plus screenshots to your coworker agent
3. Save the agent output to `qa-artifacts/agent-review/findings.json`
4. Validate schema + severity gate:
   ```bash
   npm run ui:agent:validate
   ```

Validation ensures:
- Each finding maps to an existing screenshot from the manifest
- Required fields are present (`sku`, `viewport`, `side`, `priority`, `title`, `description`, `screenshot`)
- The default severity gate fails on `P0` or `P1`

**Targeted run (single SKU):**
```bash
npm run ui:test -- -g "RG-0007"
python3 scripts/ui/build_agent_review_pack.py --sku RG-0007
```

## Automation Scripts

### validate-item.sh

**Purpose:** Pre-deployment validation to catch errors before pushing to production.

**Usage:**
```bash
./validate-item.sh RG-XXXX
```

**Exit codes:**
- 0: Validation passed (may have warnings)
- 1: Validation failed (errors found)

### audit-items.sh

**Purpose:** Comprehensive audit of all `RG-*` item folders for design consistency and completeness.

**Usage:**
```bash
./audit-items.sh
```

**Features:**
- Non-blocking (continues on errors)
- Clear, emoji-enhanced output
- Comprehensive checks across all items

## Item Card Features

### Front Side
- Item image with cream background
- SKU badge (top-right)
- Item title and era line
- Price
- "Tap to learn more" hint

### Back Side
- Story/provenance section
- Details grid (Era, Condition, Maker, Origin)
- QR code for instant payment
- "Buy Now" button linking to Square
- "Back to Collection" link

### Accessibility
- WCAG 2.1 AA compliant
- Keyboard navigation (Space/Enter to flip)
- Screen reader support with ARIA labels
- Semantic HTML structure

### Print Support
- CSS `@media print` styles for 4x6 or 5x7 card stock
- Front and back pages print separately
- Museum-quality card output for in-store displays

## Square Integration

### Payment System
- **Payment Links**: Each item has a Square payment link for instant checkout
- **QR Codes**: Generated from payment links (NOT product URLs)
- **Fulfillment**: Configured per item (shippable vs pickup-only)

### Catalog Management
- Items are added to Square catalog via `rg-full-auto` or `rg-item-update` skills
- SKU format: RG-XXXX (e.g., RG-0001, RG-0042)
- Images uploaded via `square-image-upload` skill
- Categories assigned via `catalog-classifier` skill

## Troubleshooting

### Unreplaced Placeholders

**Problem:** `{{PLACEHOLDER}}` text visible on live site

**Solution:**
- Run `./validate-item.sh RG-XXXX` to detect unreplaced placeholders
- Edit `RG-XXXX/index.html` and replace the placeholder
- Check template header for complete list of placeholders

### Large Image Files

**Problem:** Hero image > 1MB, slow page load

**Solution:**
```bash
# Re-process image with compression
# Or use ImageOptim/TinyPNG to optimize
cp optimized-image.jpeg RG-XXXX/hero.jpeg
```

### Converted Files in Git

**Problem:** `*-converted.*` files accidentally committed

**Solution:**
```bash
# Remove from tracking but keep locally
git rm --cached *-converted.*
git commit -m "Remove converted files from tracking"
```

These are already in `.gitignore` but may have been committed before the rule was added.

### QR Code Not Displaying

**Problem:** QR code broken or missing on item card

**Checklist:**
- File exists: `RG-XXXX/qr-code.png` (PNG format, not SVG)
- Path correct in index.html: `./qr-code.png`
- File size reasonable (< 100KB)
- Generated from Square payment link (not product URL)

### Flip Card Not Working

**Problem:** Card doesn't flip on click/tap

**Checklist:**
- JavaScript present in index.html
- CSS classes correct: `.flip-card`, `.card-front`, `.card-back`
- No JavaScript errors in browser console
- Test keyboard navigation (Space/Enter key)

### Item Not Appearing in Gallery

**Problem:** New item deployed but not visible on main gallery page

**Solution:**
- Gallery (`index.html`) is manually curated
- Add item to gallery grid if desired
- Or rely on direct URL: `https://richmondgeneral.github.io/items/RG-XXXX/`

## Version Control

### Branch Strategy

- **Main branch**: `main` (auto-deploys to GitHub Pages)
- Create feature branches for experimental changes
- PR workflow recommended for major updates

### Common Commands

```bash
# Check site status
git status

# Add new item
git add RG-XXXX/
git commit -m "Add RG-XXXX: [Item Name]"

# Update existing item
git add RG-XXXX/index.html
git commit -m "Update RG-XXXX: [description of change]"

# Deploy to GitHub Pages
git push origin main

# View deployment status
gh api repos/richmondgeneral/items/pages/builds/latest
```

### Deployment

Deployment is automatic via GitHub Pages:

1. Push to `main` branch
2. GitHub Actions builds site (instant, no build step)
3. Site live within 1-2 minutes
4. Check deployment status: Settings > Pages

No CI/CD configuration needed - GitHub Pages handles everything.

## Skills & External Resources

### Skills Repository

All operational skills are maintained in:
- https://github.com/richmondgeneral/skills

**Do NOT add skill definitions to this repository.** If a workflow needs a skill update, make that change in `richmondgeneral/skills`.

### Available Skills

- **rg-full-auto**: End-to-end item onboarding (appraisal → catalog → payment → publishing)
- **rg-item-update**: Quick edits to existing catalog items (price, description, images, categories)
- **image-processor**: Unified image processing with background removal and generation
- **square-image-upload**: Upload/manage images in Square Catalog via API
- **catalog-classifier**: Determines Square category assignment based on item attributes
- **book-appraiser**: Antiquarian book appraisal and valuation
- **carnival-glass-appraiser**: Carnival glass identification and valuation
- **maker-mark-identifier**: Identify maker's marks on pottery, silver, furniture, jewelry
- **product-labeler**: Generate thermal printer labels for Square inventory

See `richmondgeneral/skills` for complete skill documentation.

## Data Files

Label source of truth:
- `RG-XXXX/label.json` in each item folder

Generated batch output:
- `qa-artifacts/labels/rg-labels-batch.csv` via `npm run labels:build`

Legacy operational files (planned move to ops repo):
- `rg-inventory/rg-labels-batch.csv`
- `rg-inventory/rg-labels-batch.xlsx`
- `rg-inventory/rg-inventory-tracker.xlsx`

## Supporting Documentation

- **readme.md**: Quick start guide for users
- **SKILLS.md**: Skills migration policy and external repository link
- **template/rg-item-card-template.html**: Master template with placeholder documentation
