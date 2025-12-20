# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a **GitHub Pages site** for Richmond General, showcasing a curated vintage and antique collection with museum-style info cards. Each item gets a dedicated page with flip-card UI, story/provenance, and integrated Square payment links.

**Live Site:** [richmondgeneral.github.io/items](https://richmondgeneral.github.io/items/)

**Repository:** `git@github.com:richmondgeneral/items.git`

## Architecture

### Site Structure

```
items/
├── index.html                    # Gallery landing page
├── 404.html                      # Custom 404 "Treasure Not Found" page
├── README.md                     # Development guide
├── assets/
│   ├── favicon.svg               # RG favicon
│   └── working-images/           # Original images before processing
├── template/
│   └── rg-item-card-template.html  # Master template for new items
├── RG-0001/
│   ├── index.html                # Item card (e.g., Little Orphan Annie)
│   ├── hero.jpeg                 # Processed item image
│   └── qr-code.png               # Square payment QR code
└── RG-XXXX/
    └── index.html                # Each new item gets its own folder
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

**2. Process with square-image-upload skill:**
- Removes background
- Creates `*-converted.*` file in root (git-ignored)
- Uploads to Square catalog
- Optimizes for web

**3. Deploy to item folder:**
```bash
cp RG-XXXX-hero-converted.jpeg RG-XXXX/hero.jpeg
```

### File Naming Convention

- `RG-XXXX-hero.{jpeg|png}` - Primary item photo
- `RG-XXXX-detail.{jpeg|png}` - Close-up or alternate view
- `RG-XXXX-mark.png` - Maker's mark or signature
- `RG-XXXX-label.png` - Original labels or tags

### What's Tracked in Git

**Tracked** (version controlled):
- `assets/working-images/*` - Original source images
- `RG-XXXX/hero.{jpeg|png}` - Final deployed images
- `RG-XXXX/qr-code.png` - Payment QR codes

**Ignored** (`.gitignore`):
- `*-converted.*` - Processed images (temporary)
- `*.zip` - Archive files
- Root-level working files

## Workflow: Adding a New Item

### Automated Workflow (Recommended)

Use the automation scripts for a consistent, error-free process:

**1. Run the setup script:**
```bash
./new-item.sh
```

The script will:
- Auto-generate the next SKU (e.g., RG-0007)
- Interactively prompt for all item details
- Create the folder and index.html with placeholders replaced
- Display clear next steps

**2. Add and process images:**
```bash
# Add original to working images
cp [source] assets/working-images/RG-XXXX-hero.jpeg

# Process with square-image-upload skill
# (removes background, uploads to Square, creates *-converted.* in root)

# Move to item folder
mv RG-XXXX-hero-converted.jpeg RG-XXXX/hero.jpeg
```

**3. Generate QR code:**
- Visit Square payment link
- Generate QR code (300x300px)
- Save as `RG-XXXX/qr-code.png`

**4. Validate before deploying:**
```bash
./validate-item.sh RG-XXXX
```

Validation checks:
- Required files present (index.html, hero.*, qr-code.png)
- No unreplaced {{placeholders}}
- File sizes optimized (< 1MB recommended)
- Square payment link present
- Accessibility features

**5. Deploy:**
```bash
git add RG-XXXX
git commit -m "Add RG-XXXX: [Item Name]"
git push origin main
```

**6. Verify:**
Visit `https://richmondgeneral.github.io/items/RG-XXXX/`

### Manual Workflow (Alternative)

If not using automation scripts:

1. Create folder: `mkdir RG-XXXX`
2. Copy template: `cp template/rg-item-card-template.html RG-XXXX/index.html`
3. Manually replace all {{placeholders}} (see template header for full list)
4. Add images following ITEM_FOLDER_STRUCTURE.md
5. Run `./validate-item.sh RG-XXXX` before deploying
6. Deploy as above

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

## Integration Points

### Square Payment System

- **Payment Links**: Each item has a Square payment link for instant checkout
- **QR Codes**: Generated from payment links (NOT product URLs)
- **Fulfillment**: Configured per item (shippable vs pickup-only)

### Richmond General Ecosystem

This site is part of a larger inventory management system:

- **Main Site**: richmondgeneral.com (ecommerce)
- **Info Cards Site**: richmondgeneral.github.io/items (this repo)
- **Catalog System**: Square POS catalog
- **Inventory Tracking**: Excel/Square integration

## Automation Scripts

### new-item.sh

**Purpose:** Interactive script to scaffold new items with auto-generated SKU and placeholder replacement.

**Usage:**
```bash
./new-item.sh
```

**Features:**
- Auto-generates next SKU number (or allows custom)
- Prompts for all item details interactively
- Creates folder structure
- Generates index.html with all placeholders replaced
- Provides step-by-step next actions

**Interactive prompts:**
- SKU number (auto-suggested)
- Item title
- Era line
- Price
- Condition, maker, origin
- Square payment link
- Item story/provenance (multi-line input)
- SEO description

### validate-item.sh

**Purpose:** Pre-deployment validation to catch errors before pushing to production.

**Usage:**
```bash
./validate-item.sh RG-XXXX
```

**Checks performed:**
- ✓ Required files exist (index.html, hero.*, qr-code.png)
- ✓ No unreplaced {{placeholders}}
- ✓ Working images present in assets/working-images/
- ✓ Square payment link present
- ✓ Flip card UI and accessibility features
- ⚠ File sizes (warns if > 1MB)
- ⚠ SVG QR codes (should be PNG only)

**Exit codes:**
- 0: Validation passed (may have warnings)
- 1: Validation failed (errors found)

### audit-items.sh

**Purpose:** Comprehensive audit of all existing items for design consistency and completeness.

**Usage:**
```bash
./audit-items.sh
```

**Audits:**
- File presence and naming
- Design elements (brand colors, fonts, flip card UI)
- Square integration (payment links, QR codes)
- Accessibility features (ARIA, keyboard nav)
- Print styles

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

### Missing Working Images

**Problem:** Validation warns about missing original in assets/working-images/

**Impact:** Low - working images are for reference/re-processing

**Solution:**
```bash
# Copy original if available
cp original.jpeg assets/working-images/RG-XXXX-hero.jpeg
git add assets/working-images/RG-XXXX-hero.jpeg
```

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

## Supporting Documentation

The repository includes several reference documents:

- **README.md** - Quick start guide with automated workflow
- **ITEM_FOLDER_STRUCTURE.md** - Complete file structure specification
- **RG-Inventory-System-Requirements.md** - System architecture
- **\*.skill files** - AI assistant skills for inventory management
- **\*.xlsx files** - Inventory tracking and label generation (in rg-inventory/)

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

### File Organization Best Practices

**See ITEM_FOLDER_STRUCTURE.md for complete documentation.**

**Item Folders** (`RG-XXXX/`) - Required files:
- `index.html` - Item card HTML (REQUIRED)
- `hero.{jpeg|png}` - Final processed image (REQUIRED)
- `qr-code.png` - Square payment QR, PNG only (REQUIRED)

**Item Folders** - Optional files:
- `detail.{jpeg|png}` - Close-up or alternate view
- `mark.png` - Maker's mark or signature
- `label.png` - Original labels or tags
- Custom named images (e.g., `titlepage.jpeg`)

**Working Images** (`assets/working-images/`):
- Original photos before processing
- Naming: `RG-XXXX-[type].{jpeg|png}`
- Tracked in git (version controlled)

**Root Level**:
- Keep clean - no loose image files
- Processed `*-converted.*` files are git-ignored
- Scripts: `new-item.sh`, `validate-item.sh`, `audit-items.sh`

## Testing

### Manual Testing Checklist

For each new item card:

- [ ] All placeholders replaced
- [ ] Flip card animation works (click/tap)
- [ ] Keyboard navigation works (Space/Enter)
- [ ] Mobile responsive (test on phone)
- [ ] Payment link works
- [ ] QR code scans correctly
- [ ] Print layout renders correctly
- [ ] SEO meta tags populated
- [ ] Returns to gallery when clicking logo/back button

### Browser Testing

- Chrome/Safari (primary)
- Firefox (secondary)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

## SEO Guidelines

### URL Structure

```
https://richmondgeneral.github.io/items/RG-XXXX/
```

- Clean, semantic URLs
- Each item is indexable by search engines

### Meta Tags

- Page title: `[Item Name] | Richmond General`
- Description: 150-160 characters, include era, condition, highlights
- Open Graph tags for social sharing
- `og:type="product"` for proper rich previews

## Local Development

Since this is a static site with no build process:

```bash
# Serve locally (Python 3)
python3 -m http.server 8000

# Or use any static server
npx serve .
```

Then visit: `http://localhost:8000/RG-XXXX/`

## Deployment

Deployment is automatic via GitHub Pages:

1. Push to `main` branch
2. GitHub Actions builds site (instant, no build step)
3. Site live within 1-2 minutes
4. Check deployment status: Settings > Pages

No CI/CD configuration needed - GitHub Pages handles everything.
