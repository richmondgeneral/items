# Richmond General - Item Stories

A GitHub Pages site showcasing the curated vintage and antique collection at Richmond General, with museum-style info cards for each item.

**Live Site:** [richmondgeneral.github.io/items](https://richmondgeneral.github.io/items/)

## Structure

```
items/
├── index.html              # Main gallery/landing page
├── 404.html                # Custom 404 page
├── README.md               # This file
├── assets/
│   ├── favicon.svg         # Site favicon
│   └── og-image.jpg        # Social sharing image (add later)
├── template/
│   └── rg-item-card-template.html  # Master template for new items
├── RG-0001/
│   └── index.html          # Little Orphan Annie info card
├── RG-0002/
│   └── index.html          # Next item...
└── ...
```

## Adding a New Item

1. **Create folder:** `mkdir RG-XXXX`

2. **Copy template:** 
   ```bash
   cp template/rg-item-card-template.html RG-XXXX/index.html
   ```

3. **Replace placeholders** in the new `index.html`:
   - `{{SKU}}` → `RG-XXXX`
   - `{{ITEM_TITLE}}` → Full item title
   - `{{ERA_LINE}}` → e.g., "1930s Americana · 1979 Dover Reprint"
   - `{{PRICE}}` → e.g., `19.99`
   - `{{STORY_TEXT}}` → The item's history and provenance
   - `{{ERA}}` → e.g., "1930s"
   - `{{CONDITION}}` → e.g., "Very Good"
   - `{{MAKER}}` → e.g., "Dover Publications"
   - `{{ORIGIN}}` → e.g., "USA"
   - `{{IMAGE_URL}}` → Path to item image
   - `{{QR_CODE_URL}}` → Path to payment QR code image
   - `{{PAYMENT_LINK_URL}}` → Square payment link (square.link/u/...)
   - `{{SEO_DESCRIPTION}}` → 150-160 char description

4. **Add to gallery** - Edit `index.html` and add a new item card in the `.items-grid` section

5. **Commit & push:**
   ```bash
   git add .
   git commit -m "Add RG-XXXX [Item Name]"
   git push origin main
   ```

6. **Verify:** Visit `https://richmondgeneral.github.io/items/RG-XXXX/`

## Item Card Features

- **Flip interaction** - Tap/click to flip between front (image/price) and back (story/details)
- **QR code** - Links to Square payment for instant checkout
- **Print-ready** - Cards render correctly for 4x6 or 5x7 card stock
- **WCAG 2.1 AA accessible** - Keyboard navigation, screen reader support
- **Mobile responsive** - Works on all device sizes
- **SEO optimized** - Open Graph tags, semantic HTML

## Branding

**Colors:**
- Gold: `#C9A961`
- Cream: `#F5F1E8`
- Charcoal: `#2C2C2C`
- Brown: `#6B4423`

**Fonts:**
- Headings: Playfair Display
- Body: Source Sans Pro

## Integration

Each item card integrates with:
- **Square** - Payment links for direct checkout
- **Richmond General main site** - Links back to richmondgeneral.com
- **Analytics** - Event hooks ready for tracking (see template JS)

## License

© 2024-2025 Richmond General. All rights reserved.
