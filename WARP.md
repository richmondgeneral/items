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
│   └── favicon.svg               # RG favicon
├── template/
│   └── rg-item-card-template.html  # Master template for new items
├── RG-0001/
│   └── index.html                # Item card (e.g., Little Orphan Annie)
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

## Workflow: Adding a New Item

### 1. Create Item Folder

```bash
mkdir RG-XXXX
```

### 2. Copy Template

```bash
cp template/rg-item-card-template.html RG-XXXX/index.html
```

### 3. Replace Placeholders

Edit `RG-XXXX/index.html` and replace all template variables:

- `{{SKU}}` → Item SKU (e.g., `RG-0002`)
- `{{ITEM_TITLE}}` → Full item title
- `{{ERA_LINE}}` → Era description (e.g., "1930s Americana · 1979 Dover Reprint")
- `{{PRICE}}` → Price (e.g., `19.99`)
- `{{STORY_TEXT}}` → The item's history, provenance, and description
- `{{ERA}}` → Era value for details grid (e.g., "1930s")
- `{{CONDITION}}` → Condition grade (e.g., "Very Good")
- `{{MAKER}}` → Maker/publisher/manufacturer
- `{{ORIGIN}}` → Origin/location (e.g., "USA")
- `{{IMAGE_URL}}` → Path to item image
- `{{QR_CODE_URL}}` → Path to payment QR code image
- `{{PAYMENT_LINK_URL}}` → Square payment link (square.link/u/...)
- `{{SEO_DESCRIPTION}}` → 150-160 character meta description

### 4. Add to Gallery (Optional)

Edit `index.html` to add the item to the gallery grid.

### 5. Deploy

```bash
git add .
git commit -m "Add RG-XXXX [Item Name]"
git push origin main
```

GitHub Pages will automatically deploy the changes. The item will be live at:
`https://richmondgeneral.github.io/items/RG-XXXX/`

### 6. Verify

Visit the live URL to verify:
- Flip card interaction works
- All placeholder text replaced
- QR code displays correctly
- Payment link works
- Mobile responsiveness
- Print layout (if printing cards)

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

## Supporting Documentation

The repository includes several reference documents:

- **README.md** - Quick start guide for adding items
- **RG-Inventory-System-Requirements.md** - Complete system architecture
- **\*.skill files** - AI assistant skills for inventory management
- **\*.xlsx files** - Inventory tracking and label generation

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

- One folder per SKU: `RG-XXXX/`
- Store images in item folder if needed: `RG-XXXX/images/`
- Keep QR codes with item: `RG-XXXX/qr/`
- Archive sold items to `_archive/` (not currently implemented)

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
