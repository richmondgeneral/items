# Richmond General - Item Stories

A GitHub Pages site showcasing the curated vintage and antique collection at Richmond General, with museum-style info cards for each item.

**Live Site:** [richmondgeneral.github.io/items](https://richmondgeneral.github.io/items/)
**Skills Repo:** [github.com/richmondgeneral/skills](https://github.com/richmondgeneral/skills)

## Structure

```
items/
├── index.html              # Main gallery/landing page
├── 404.html                # Custom 404 page
├── readme.md               # This file
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

### Automated Workflow (Recommended)

1. **Run the setup script:**
   ```bash
   ./new-item.sh
   ```
   
   The script will:
   - Auto-generate the next SKU number (or let you specify one)
   - Prompt for all item details interactively
   - Create the item folder
   - Generate `index.html` with all placeholders replaced
   - Display next steps for images and deployment

2. **Add and process item image:**
   ```bash
   # Add original image to working directory
   cp [source-image] assets/working-images/RG-XXXX-hero.jpeg
   
   # Process with square-image-upload skill (removes background, uploads to Square)
   # This creates RG-XXXX-hero-converted.jpeg in root (git-ignored)
   
   # Move processed image to item folder
   mv RG-XXXX-hero-converted.jpeg RG-XXXX/hero.jpeg
   ```

3. **Generate QR code:**
   - Visit your Square payment link
   - Generate QR code (300x300px recommended)
   - Save as `RG-XXXX/qr-code.png`

4. **Validate before deploying:**
   ```bash
   ./validate-item.sh RG-XXXX
   ```
   
   This checks for:
   - Required files (index.html, hero image, qr-code.png)
   - Unreplaced placeholders
   - File sizes and optimization
   - Content completeness

5. **Deploy to GitHub Pages:**
   ```bash
   git add RG-XXXX
   git commit -m "Add RG-XXXX: [Item Name]"
   git push origin main
   ```

6. **Verify:** Visit `https://richmondgeneral.github.io/items/RG-XXXX/`

### Manual Workflow (Alternative)

1. **Create folder:** `mkdir RG-XXXX`

2. **Copy template:** 
   ```bash
   cp template/rg-item-card-template.html RG-XXXX/index.html
   ```

3. **Replace placeholders** - See `template/rg-item-card-template.html` header for complete list

4. **Add images** - Follow image workflow in ITEM_FOLDER_STRUCTURE.md

5. **Validate:** `./validate-item.sh RG-XXXX`

6. **Deploy:** Commit and push as above

## Scripts

### `./new-item.sh`
Interactive script to scaffold a new item from template. Auto-generates SKU, creates folder, replaces placeholders.

### `./validate-item.sh RG-XXXX`
Validates an item folder before deployment. Checks for required files, unreplaced placeholders, file sizes, and content completeness.

### `./audit-items.sh`
Audits all existing items for design elements, accessibility features, and content completeness.

## Skills

Item-processing skills are maintained in the separate `richmondgeneral/skills` repository.
This repo focuses on the deployed item pages, static assets, and inventory data files.

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
