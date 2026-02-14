# Working Images Directory

This directory contains source/original images for Richmond General items before processing and deployment.

## Directory Purpose

- **Originals**: High-quality source images before background removal or optimization
- **Detail shots**: Additional photos for documentation (not always published)
- **Labels/marks**: Close-ups of maker's marks, labels, or identifying features
- **Working files**: Images in progress before final deployment to item folders

## Workflow

### 1. Add Original Images Here

```bash
# Place original photos in this directory
cp ~/Desktop/new-item-photo.jpeg assets/working-images/RG-XXXX-hero.jpeg
```

### 2. Process Images

Use the **square-image-upload** skill to:
- Remove backgrounds (creates `*-converted.*` files in root)
- Optimize for web
- Upload to Square catalog

### 3. Deploy to Item Folder

After processing, final images go to the item's folder:

```bash
cp RG-XXXX-hero-converted.jpeg RG-XXXX/hero.jpeg
```

## File Naming Convention

- `RG-XXXX-hero.{jpeg|png}` - Primary item photo
- `RG-XXXX-detail.{jpeg|png}` - Close-up or alternate view
- `RG-XXXX-mark.png` - Maker's mark or signature
- `RG-XXXX-label.png` - Original labels or tags
- `RG-XXXX-{context}.{jpeg|png}` - Any other relevant photos

## Git Tracking

**This directory IS tracked** in version control to preserve original source images.

**Root-level processed files are NOT tracked**:
- `*-converted.*` files (ignored by `.gitignore`)
- `*.zip` archives
- Temporary working files

## Image Requirements

### Hero Images (Primary Photos)

- **Format**: JPEG or PNG
- **Resolution**: Min 1200px on longest side
- **Aspect Ratio**: Flexible (square-image-upload handles cropping)
- **Background**: Any (will be removed during processing)

### Detail Images (Optional)

- **Purpose**: Showcase condition, features, marks
- **Format**: JPEG or PNG
- **Usage**: Documentation, may not be published

## Storage Size

Current directory size and file count change as inventory grows; check with `du -sh` and `ls`.

Original images are compressed JPEG/PNG suitable for web deployment after processing.

## Related Documentation

- **CLAUDE.md** - Full architecture and workflow guidance for agents
- **readme.md** (root) - Item card creation guide
- **square-image-upload skill** - Background removal automation
