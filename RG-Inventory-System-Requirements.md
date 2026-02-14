# Richmond General Inventory System
## Current Requirements Baseline

Last updated: 2026-02-14

## Purpose

This repository supports the Richmond General item-story site and related inventory artifacts.
It is the source of truth for:
- GitHub Pages item cards (`RG-XXXX/index.html`)
- Item media used by the site (`hero.*`, `qr-code.png`)
- Inventory label/data files used in operations

## Repository Scope

In scope for `richmondgeneral/items`:
- Static site pages and templates
- Item folders (`RG-XXXX`)
- Supporting scripts (`new-item.sh`, `validate-item.sh`, `audit-items.sh`, `test-css-requirements.sh`)
- Inventory data files in repo (`rg-labels-batch.csv`, `rg-inventory/*`)

Out of scope for this repo:
- Skill definitions and skill reference packs
- Reusable skill automation logic

## Skills Ownership

All skills are maintained in:
- https://github.com/richmondgeneral/skills

Rules:
- Do not add `SKILL.md` definitions to this repository.
- Do not add skill reference trees here unless they are also required as normal project docs.
- Skill changes should be made in `richmondgeneral/skills` and versioned there.

## Item Folder Contract

Each published item folder should contain:
- `index.html`
- `hero.jpeg` or `hero.png`
- `qr-code.png`

Operational expectations:
- Buy button points to a real destination (prefer Square payment link when listed)
- No placeholder template tokens in HTML
- Print CSS present for card output

## Validation Requirements

Required checks before deploy:

```bash
./validate-item.sh RG-XXXX
./test-css-requirements.sh RG-XXXX
```

Repository-wide checks:

```bash
./audit-items.sh
for d in RG-*; do [ -d "$d" ] && ./validate-item.sh "$d" || true; done
```

## Deployment Requirements

Deployment path:
1. Update or add item files.
2. Validate item and run audit.
3. Commit and push to `main`.
4. Verify live page under `https://richmondgeneral.github.io/items/RG-XXXX/`.

## Data File Locations

Primary tracked label/inventory files in this repo:
- `/Users/scottybe/workspace/square/items/rg-labels-batch.csv`
- `/Users/scottybe/workspace/square/items/rg-inventory/rg-labels-batch.csv`
- `/Users/scottybe/workspace/square/items/rg-inventory/rg-labels-batch.xlsx`
- `/Users/scottybe/workspace/square/items/rg-inventory/rg-inventory-tracker.xlsx`

## Notes

This document replaces older design content that referenced local skill folders that are no longer hosted in this repository.
