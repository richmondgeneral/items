# Testing Guide for Richmond General Item Cards

## Quick Item Check

Run these commands before committing changes to an item card:

```bash
./validate-item.sh RG-XXXX
./test-css-requirements.sh RG-XXXX
```

What they cover:
- Required files (`index.html`, `hero.*`, `qr-code.png`)
- Placeholder replacement
- Square link presence
- Core card CSS/layout requirements
- Basic accessibility and print-style checks

## Repository-Wide Checks

Run a full audit and validate all item folders:

```bash
./audit-items.sh

for d in RG-*; do
  [ -d "$d" ] || continue
  ./validate-item.sh "$d" || true
done
```

## Local Preview

Serve locally and test in browser:

```bash
python3 -m http.server 8000
```

Then visit:
- `http://localhost:8000/`
- `http://localhost:8000/RG-XXXX/`

## Manual QA Checklist

For each changed item page:
- Flip interaction works with click/tap and keyboard
- Front/back content is readable on desktop and mobile widths
- Buy button points to a real destination (not `#`)
- Hero image and QR code render correctly
- Print stylesheet exists and produces usable output

## Pre-Deploy Sequence

```bash
./validate-item.sh RG-XXXX
./test-css-requirements.sh RG-XXXX
./audit-items.sh
git add <changed-files>
git commit -m "..."
git push origin main
```

## Optional Advanced Automation

Visual regression or DOM-assertion scripts are optional and not included in this repository by default. If you add them, document their exact filenames and commands in this file at the same time.
