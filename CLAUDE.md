# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **GitHub Pages site** for Richmond General, showcasing a curated vintage and antique collection with museum-style info cards. It's a static HTML/CSS/JavaScript site with no build process, designed for simplicity and direct deployment.

**Live Site:** [richmondgeneral.github.io/items](https://richmondgeneral.github.io/items/)
**Skills Repo:** [github.com/richmondgeneral/skills](https://github.com/richmondgeneral/skills)

## Common Development Commands

### Workflow Scripts
- **Create new item**: `./new-item.sh` - Interactive script to scaffold new items with auto-generated SKU
- **Validate item**: `./validate-item.sh RG-XXXX` - Pre-deployment validation checks
- **Audit all items**: `./audit-items.sh` - Check design consistency and completeness

### Local Development
```bash
# Serve locally (no build required - static site)
python3 -m http.server 8000
# Visit: http://localhost:8000/RG-XXXX/
```

### Deployment
```bash
# Deployment is automatic via GitHub Pages
git add RG-XXXX
git commit -m "Add RG-XXXX: [Item Name]"
git push origin main
# Site updates within 1-2 minutes
```

## High-Level Architecture

### Project Structure
```
items/
├── index.html              # Gallery landing page
├── 404.html                # Custom 404 page
├── template/
│   └── rg-item-card-template.html  # Master template for new items
├── new-item.sh             # Create new item from template
├── validate-item.sh        # Validate item before deployment
├── audit-items.sh          # Audit all items for consistency
├── assets/
│   ├── favicon.svg         # Site favicon
│   └── working-images/     # Original images before processing
├── rg-inventory/           # Inventory management files
│   ├── rg-inventory-tracker.xlsx
│   └── rg-labels-batch.csv
└── RG-XXXX/               # Individual item folders
    ├── index.html         # Item card page
    ├── hero.jpeg          # Processed item image
    └── qr-code.png        # Square payment QR code
```

### Technology Stack
- **Framework**: Pure HTML/CSS/JavaScript (no build step, no dependencies)
- **Hosting**: GitHub Pages (automatic deployment from main branch)
- **Fonts**: Google Fonts (Playfair Display, Source Sans Pro)
- **Interactive Elements**: Vanilla JavaScript for flip card animation
- **Integrations**: Square payment links and QR codes

### Key Design Components

**Item Card Features:**
- Flip-card interaction (tap/click to flip between front and back)
- Front: Item image, SKU badge, title, price
- Back: Story/provenance, details grid, QR code, payment link
- Mobile responsive design
- Print-ready CSS for physical card stock

**Brand Design System:**
```css
--rg-gold: #C9A961
--rg-cream: #F5F1E8
--rg-charcoal: #2C2C2C
--rg-brown: #6B4423
```

## Adding New Items Workflow

### Automated Workflow (Recommended)
1. **Run setup script**: `./new-item.sh`
   - Auto-generates next SKU or accepts custom SKU
   - Prompts for all item details interactively
   - Creates folder and populated index.html

2. **Process item image**:
   ```bash
   # Add original to working directory
   cp [source] assets/working-images/RG-XXXX-hero.jpeg
   
   # Process with square-image-upload skill
   # Creates RG-XXXX-hero-converted.jpeg in root
   
   # Deploy to item folder
   mv RG-XXXX-hero-converted.jpeg RG-XXXX/hero.jpeg
   ```

3. **Add payment QR code**:
   - Generate from Square payment link (300x300px)
   - Save as `RG-XXXX/qr-code.png` (PNG format only)

4. **Validate and deploy**:
   ```bash
   ./validate-item.sh RG-XXXX
   git add RG-XXXX
   git commit -m "Add RG-XXXX: [Item Name]"
   git push origin main
   ```

### Image Management
- **Working images**: Store originals in `assets/working-images/RG-XXXX-*.jpeg`
- **Processed images**: Background removed, web-optimized
- **Git-ignored**: `*-converted.*` files in root (temporary processing files)
- **Required files**: `hero.{jpeg|png}`, `qr-code.png` in each item folder

### Validation Checks
The `validate-item.sh` script ensures:
- Required files exist (index.html, hero image, QR code)
- No unreplaced {{placeholders}} in HTML
- File sizes are optimized (< 1MB recommended)
- Square payment link is present
- QR code is PNG format (not SVG)

## Square Integration

Each item integrates with Square for payments:
- **Payment Links**: Direct checkout via square.link URLs
- **QR Codes**: Generated from payment links for mobile scanning
- **Catalog**: Items are added to Square catalog with the square-image-upload skill
- **SKU Format**: RG-XXXX (e.g., RG-0001, RG-0042)

## Important Files

- **readme.md**: Quick start guide and project overview
- **WARP.md**: Extended documentation for WARP terminal users
- **ITEM_FOLDER_STRUCTURE.md**: Detailed file organization specification
- **template/rg-item-card-template.html**: Master template with all placeholders documented
- **SKILLS.md**: Skill migration status and canonical skills repository
