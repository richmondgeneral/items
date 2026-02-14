# Item Folder Structure

This document defines the standard file structure for each item folder in the repository.

## Required Files

Every item folder (`RG-XXXX/`) MUST contain:

```
RG-XXXX/
├── index.html         # Item card page (from template)
├── hero.{jpeg|png}    # Primary item image (processed, background removed)
└── qr-code.png        # Square payment QR code (PNG format only)
```

### File Requirements

- **index.html**: Generated from `template/rg-item-card-template.html` with all `{{placeholders}}` replaced
- **hero.{jpeg|png}**: Processed image (background removed, optimized for web)
  - Prefer JPEG for photographs
  - Use PNG for items with transparency or sharp edges
  - Should be optimized for web (< 1MB recommended)
- **qr-code.png**: QR code linking to Square payment page
  - Must be PNG format (NOT SVG)
  - Generated from Square payment link (not product catalog URL)

## Optional Files

Item folders MAY contain additional images for detail views:

```
RG-XXXX/
├── detail.{jpeg|png}  # Close-up or alternate view
├── mark.png           # Maker's mark, signature, or stamp
├── label.png          # Original labels, tags, or certificates
└── [custom].{jpeg|png} # Other specific images (e.g., titlepage.jpeg, polarbear.jpeg)
```

### Optional File Guidelines

- Use descriptive names for custom images (e.g., `titlepage.jpeg`, `polarbear.jpeg` for RG-0002)
- Prefer PNG for marks/labels (usually have transparency or need sharp text)
- Keep file sizes optimized for web
- Optional files are NOT automatically displayed on item cards (require custom HTML edits)

## Working Images Directory

Original/source images are stored in `assets/working-images/`:

```
assets/working-images/
├── RG-XXXX-hero.{jpeg|png}      # Original image before processing
├── RG-XXXX-detail.{jpeg|png}    # Detail shot original
├── RG-XXXX-mark.png             # Maker's mark original
└── RG-XXXX-label.png            # Label original
```

### Working Images Workflow

1. Add original images to `assets/working-images/RG-XXXX-[type].{jpeg|png}`
2. Process with square-image-upload skill (removes background, uploads to Square)
3. Processed images appear as `RG-XXXX-[type]-converted.*` in root (git-ignored)
4. Deploy final images to item folder: `RG-XXXX/[type].{jpeg|png}`
5. Working images remain in `assets/working-images/` (tracked in git)
6. Converted files can be deleted after deployment (not tracked in git)

## Naming Conventions

### Item Folders
- Format: `RG-XXXX` where XXXX is a zero-padded 4-digit number
- Examples: `RG-0001`, `RG-0042`, `RG-1234`

### Images in Item Folders
- Required: `hero.{jpeg|png}`, `qr-code.png`
- Optional standard: `detail.{jpeg|png}`, `mark.png`, `label.png`
- Custom: Use descriptive lowercase names with hyphens (e.g., `title-page.jpeg`)

### Images in Working Directory
- Format: `RG-XXXX-[type].{jpeg|png}`
- Examples: `RG-0001-hero.jpeg`, `RG-0004-mark.png`
- Type should match deployment name (hero, detail, mark, label, etc.)

## Examples

### Minimal Item (Standard)
```
RG-0003/
├── index.html
├── hero.jpeg
└── qr-code.png
```

### Item with Additional Details
```
RG-0002/
├── index.html
├── hero.jpeg
├── qr-code.png
├── polarbear.jpeg    # Custom image
└── titlepage.jpeg    # Custom image
```

### Item with Maker's Mark
```
RG-0004/
├── index.html
├── hero.jpeg
├── qr-code.png
└── mark.png         # Maker's mark/signature
```

## Validation

Before deploying a new item, verify:

- [ ] Item folder named `RG-XXXX` (4 digits, zero-padded)
- [ ] `index.html` exists with all `{{placeholders}}` replaced
- [ ] `hero.{jpeg|png}` exists and is optimized
- [ ] `qr-code.png` exists (PNG format only, no SVG)
- [ ] Optional images follow naming convention
- [ ] Original images stored in `assets/working-images/`
- [ ] No `-converted.*` files committed to git

## Current Repository Status

Repository inventory changes frequently. Use runtime checks instead of static counts:
- `./validate-item.sh RG-XXXX` for item-level validation
- `./audit-items.sh` for repository-wide audits across all `RG-*` folders
