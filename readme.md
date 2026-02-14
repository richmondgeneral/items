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
│   └── working-images/     # Source images before processing/deploy
├── template/
│   └── rg-item-card-template.html  # Master template for new items
├── scripts/
│   └── labels/build_batch_csv.py    # Build batch label CSV from RG-*/label.json
├── RG-0001/
│   ├── index.html          # Item card page
│   ├── hero.{jpeg|png}     # Item image
│   ├── qr-code.png         # Payment QR
│   └── label.json          # Label metadata
├── RG-0002/
│   └── index.html          # Next item...
└── ...
```

## Adding a New Item

### Automated Workflow (Recommended)

Use the **rg-full-auto** skill for complete item onboarding:

1. **Load photo into Claude** (AirDrop or drag/drop)
2. **Say "new item"** or "add to inventory"
3. **Supervise the workflow:**
   - Phase 1: Appraisal & pricing (approve)
   - Phase 2: Background removal
   - Phase 3: Square catalog creation (approve)
   - Phase 4: Image upload
   - Phase 5: Payment link generation
   - Phase 6: Label metadata generation (`RG-XXXX/label.json`)
   - Phase 7: GitHub Pages deployment (approve)

**Output:**
- Square catalog item
- Payment link (square.link/u/XXXXXXXX)
- Item-level `label.json` metadata
- GitHub Pages card
- Files organized in `RG-XXXX/` folder

**Requirements:**
- `SQUARE_ACCESS_TOKEN` environment variable
- `REMOVEBG_API_KEY` environment variable

See **CLAUDE.md** for complete workflow documentation.

### Manual Workflow (Alternative)

1. **Create folder:** `mkdir RG-XXXX`
2. **Copy template:** `cp template/rg-item-card-template.html RG-XXXX/index.html`
3. **Replace placeholders:** See template header for complete list
4. **Add images + label metadata:** Follow structure in CLAUDE.md
5. **Validate:** `./validate-item.sh RG-XXXX`
6. **Deploy:**
   ```bash
   git add RG-XXXX
   git commit -m "Add RG-XXXX: [Item Name]"
   git push origin main
   ```

### Label Metadata

Each item folder should include `label.json` with:
- `sku`
- `product_name`
- `attributes`
- `price`
- `condition`
- `condition_notes`
- `qr_code_url`

Build a batch CSV for printing labels:

```bash
npm run labels:build
```

## Scripts

### `./validate-item.sh RG-XXXX`
Validates an item folder before deployment. Checks for required files, unreplaced placeholders, file sizes, and content completeness.

### `./audit-items.sh`
Audits all existing items for design elements, accessibility features, and content completeness.

### `npm run labels:build`
Builds `qa-artifacts/labels/rg-labels-batch.csv` from all `RG-*/label.json` files.

### `npm run ui:review`
Runs Playwright screenshot QA (desktop/mobile, front/back) and builds an agent-review pack in `qa-artifacts/agent-review/`.

### `npm run ui:agent:validate`
Validates `qa-artifacts/agent-review/findings.json` from a coworker agent against the screenshot manifest and fails on `P0/P1` findings by default.

## Skills

Item-processing skills are maintained in the separate `richmondgeneral/skills` repository.
This repo focuses on deployed item pages, static assets, and item-level label metadata.
Financial tracking (lot costs, ROI, margin analysis) lives in the private ops repository.

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
