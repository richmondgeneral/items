# Richmond General Inventory System
## Requirements & Design Document
### Version 1.1 | November 26, 2025

---

# Table of Contents

1. [System Overview](#1-system-overview)
2. [Skill Architecture](#2-skill-architecture)
3. [Complete Workflow](#3-complete-workflow)
4. [Data Structures](#4-data-structures)
5. [API Integrations](#5-api-integrations)
6. [Business Logic](#6-business-logic)
7. [File Organization](#7-file-organization)
8. [Verification Checklist](#8-verification-checklist)
9. [Appendix: Reference Data](#appendix-reference-data)

---

# 1. System Overview

## 1.1 Purpose

Automate the complete inventory workflow for Richmond General antique/vintage store:
- Item appraisal and research
- Square catalog management
- Pricing and fulfillment configuration
- Payment link generation
- Label/QR code creation
- **Info card creation (museum-style placards)**
- **GitHub Pages publishing**
- Asset organization

## 1.2 Key Principles

1. **Payment Links for QR codes** - NOT product URLs
2. **Shipping logic based on item characteristics** - Easy ship vs pickup only
3. **Modular skills** - Specialist routing for books, vintage marks, etc.
4. **Organized file storage** - Item folders with all assets together
5. **Full traceability** - Lot tracking, metadata, version history

## 1.3 System Components

| Component | Purpose | Status |
|-----------|---------|--------|
| rg-inventory | Main orchestrator skill | Active |
| vintage-appraiser | Maker's mark identification | Active |
| book-appraiser | Antiquarian book appraisal | Active |
| product-labeler | Label generation for Print Master | Active |
| imessage-assistant | Customer/vendor communication | Active |

---

# 2. Skill Architecture

## 2.1 Skill Hierarchy

```
rg-inventory (orchestrator)
├── vintage-appraiser (marks, glass, pottery, silver)
│   ├── references/research-sources.md
│   ├── references/carnival-glass.md
│   ├── references/pricing-research.md
│   └── references/listing-descriptions.md
├── book-appraiser (antiquarian books)
│   └── references/condition-grading.md
└── product-labeler (thermal labels)
    ├── references/style-guide.md
    └── scripts/generate_label.py
```

## 2.2 Skill Routing Rules

### Route to vintage-appraiser when:
- [ ] Item needs maker's mark identification
- [ ] Image shows pottery/glass/silver/furniture mark
- [ ] Item needs pattern identification or dating
- [ ] Researching carnival glass, pottery, or antiques
- [ ] User mentions Northwood, Fenton, Imperial, Dugan, Millersburg

### Route to book-appraiser when:
- [ ] Item is a book, pamphlet, or printed publication
- [ ] Book appears pre-1970 (no ISBN, old binding)
- [ ] User asks about editions, printings, or book value
- [ ] Need to check Library of Congress holdings
- [ ] User mentions Dover, Scribner's, or other publishers

### Route to product-labeler when:
- [ ] User requests label generation
- [ ] Item is ready for floor (has SKU, price, payment link)
- [ ] Batch label printing needed

## 2.3 Required Skill Files

### rg-inventory
```
rg-inventory/
├── SKILL.md                          # REQUIRED
└── references/
    ├── pricing-guidelines.md         # REQUIRED
    ├── lot-tracking.md               # REQUIRED
    ├── square-catalog.md             # REQUIRED
    └── label-format.md               # REQUIRED
```

### vintage-appraiser
```
vintage-appraiser/
├── SKILL.md                          # REQUIRED
└── references/
    ├── research-sources.md           # REQUIRED
    ├── carnival-glass.md             # REQUIRED
    ├── pricing-research.md           # REQUIRED
    └── listing-descriptions.md       # REQUIRED
```

### book-appraiser
```
book-appraiser/
├── SKILL.md                          # REQUIRED
└── references/
    └── condition-grading.md          # REQUIRED
```

---

# 3. Complete Workflow

## 3.1 End-to-End Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITEM PROCESSING WORKFLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ PHASE 1  │───▶│ PHASE 2  │───▶│ PHASE 3  │───▶│ PHASE 4  │  │
│  │ Appraise │    │ Photo    │    │ Catalog  │    │ Fulfill  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                                                │         │
│       ▼                                                ▼         │
│  ┌──────────┐                                    ┌──────────┐   │
│  │ PHASE 5  │◀───────────────────────────────────│ PHASE 6  │   │
│  │ Payment  │                                    │ Label    │   │
│  │ Link     │───────────────────────────────────▶│ & File   │   │
│  └──────────┘                                    └──────────┘   │
│       │                                                │         │
│       └────────────────────┬───────────────────────────┘         │
│                            ▼                                     │
│                      ┌──────────┐                                │
│                      │ PHASE 7  │                                │
│                      │ Info Card│                                │
│                      │ & Publish│                                │
│                      └──────────┘                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 Phase Details

### Phase 1: Appraisal & Research
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 1.1 | Identify item type | Category determination | Manual/AI |
| 1.2 | Route to specialist | Specialist skill loaded | rg-inventory routing |
| 1.3 | Research maker/origin | Identification | vintage-appraiser OR book-appraiser |
| 1.4 | Research market value | Price comps | web_search (eBay sold, AbeBooks) |
| 1.5 | Determine condition | Condition grade | Specialist skill |
| 1.6 | Calculate price | Final price | pricing-guidelines.md |

### Phase 2: Photography & Images
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 2.1 | Photograph item | Raw images | Camera |
| 2.2 | Process images | Edited images | rembg (background removal) |
| 2.3 | Create item folder | Folder structure | File system |
| 2.4 | Store images | Organized files | /items/SKU/images/ |

### Phase 3: Square Catalog Creation
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 3.1 | Assign SKU | RG-XXXX | Sequential numbering |
| 3.2 | Create catalog item | Item ID | catalog.batchInsertObjects |
| 3.3 | Upload image | Image ID | Catalog images API |
| 3.4 | Set inventory count | Count = 1 | inventory.batchChange |
| 3.5 | Configure SEO | Permalink, title, desc | catalog.batchUpdateObjects |
| 3.6 | Assign categories | Category IDs | Include in creation |

### Phase 4: Fulfillment Setup
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 4.1 | Assess shippability | Ship or Pickup-only | Business logic |
| 4.2 | Assign shipping box | Box assignment | Square Dashboard (manual) |
| 4.3 | Enable fulfillment methods | Fulfillment config | Square Dashboard (manual) |

### Phase 5: Payment Link Generation
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 5.1 | Create payment link | Link ID + URL | checkout.createPaymentLink |
| 5.2 | Generate QR code | PNG file | qrcode library |
| 5.3 | Store QR code | /items/SKU/qr/ | File system |

### Phase 6: Label & File Organization
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 6.1 | Create metadata.json | Item record | File system |
| 6.2 | Generate label CSV | Print Master data | product-labeler |
| 6.3 | Print label | Physical label | Thermal printer |
| 6.4 | Update completed log | Tracking record | rg-inventory |

### Phase 7: Info Card & Publishing (Museum Experience)
| Step | Action | Output | Tool/Skill |
|------|--------|--------|------------|
| 7.1 | Generate info card HTML | index.html | rg-item-card-template |
| 7.2 | Write story/provenance | Story text | AI + research |
| 7.3 | Insert actual QR code | QR PNG embedded | From Phase 5 |
| 7.4 | Deploy to GitHub Pages | Live URL | Git push |
| 7.5 | Print card (optional) | 4x6 or 5x7 card | Card stock printer |
| 7.6 | Place in acrylic stand | In-store display | Manual |

**Info Card Purpose:**
- **In-store**: Museum-style placard next to item, tells the STORY
- **Online**: SEO-indexed page, educational content, links to purchase
- **Collector appeal**: History and provenance build value perception

**Info Card Content Hierarchy:**

| Level | Format | Content | Location |
|-------|--------|---------|----------|
| Label | 2x1" tag | SKU, price, QR | On/near item |
| Info Card | Flip card | Story, history, maker, era, QR, buy button | Next to item / GitHub |
| Listing | Square page | Full description, shipping, buy | richmondgeneral.com |

**GitHub Pages Structure:**
```
richmondgeneral.github.io/items/
├── RG-0001/
│   └── index.html    → richmondgeneral.github.io/items/RG-0001/
├── RG-0002/
│   └── index.html
└── template/
    └── rg-item-card-template.html
```

**Info Card Template Features:**
- Flip card interaction (tap to see story)
- Front: Image, title, era, price
- Back: Story, details grid (era, condition, maker, origin), QR code, buy button
- WCAG 2.1 AA accessible
- Print-ready (4x6 or 5x7 card stock)
- Richmond General branding (gold/cream/charcoal palette)
- Analytics hooks for tracking engagement

---

# 4. Data Structures

## 4.1 Item Metadata Schema

```json
{
    "sku": "RG-0001",
    "title": "Full item title",
    "description": "Full description for catalog",
    "price_cents": 1999,
    "condition": "Very Good",
    "category": "Books",
    
    "square_ids": {
        "item_id": "2A2VL6JA6VHOQLRLERFR5BZJ",
        "variation_id": "UQORP6UPBOGGNDKOE4GU2M2J",
        "image_id": "CQPVYM6AJ4UB4Q56LFLWBHGV"
    },
    
    "payment_link": {
        "id": "ABCD1234",
        "url": "https://square.link/u/XXXXXXX",
        "created_at": "2025-11-26T12:00:00Z"
    },
    
    "urls": {
        "payment_link": "https://square.link/u/XXXXXXX",
        "product_page": "https://www.richmondgeneral.com/product/permalink/item_id",
        "info_card": "https://richmondgeneral.github.io/items/RG-0001/",
        "qr_code_source": "payment_link"
    },
    
    "info_card": {
        "story_text": "The narrative history and provenance of the item",
        "era_line": "1930s Americana · 1979 Dover Reprint",
        "maker": "Dover Publications",
        "origin": "USA",
        "github_path": "items/RG-0001/index.html",
        "deployed": true
    },
    
    "seo": {
        "permalink": "keyword-rich-slug",
        "page_title": "SEO Title | Category",
        "page_description": "150-160 char description"
    },
    
    "fulfillment": {
        "shippable": true,
        "shipping_box": "Small Flat Rate",
        "methods_enabled": ["shipping", "pickup", "local_delivery"]
    },
    
    "provenance": {
        "source_lot": "PETER-002",
        "cost_allocation": 5.00,
        "acquired_date": "2025-11-19"
    },
    
    "files": {
        "images": [
            "images/RG-0001-main.jpg",
            "images/RG-0001-nobg.png"
        ],
        "qr_code": "qr/RG-0001-payment-qr.png",
        "label_csv": "label/RG-0001-label.csv"
    },
    
    "status": "listed",
    "created_at": "2025-11-26T12:00:00Z",
    "updated_at": "2025-11-26T12:00:00Z"
}
```

## 4.2 SKU Format

**Pattern:** `RG-XXXX`
- Prefix: `RG` (Richmond General)
- Separator: `-`
- Number: 4-digit sequential, zero-padded

**Examples:**
- RG-0001, RG-0002, ..., RG-9999

## 4.3 Lot ID Format

**Pattern:** `{SOURCE}-{IDENTIFIER}`

| Source Type | Example | Description |
|-------------|---------|-------------|
| Person | PETER-002 | Seller name + visit number |
| Location | IOWA-0925 | Location + date (MMYY) |
| Estate | ESTATE-SMITH | Estate + family name |
| Auction | AUCTION-12345 | Auction + lot number |

---

# 5. API Integrations

## 5.1 Square API Endpoints

### Required Endpoints

| Endpoint | Purpose | Phase |
|----------|---------|-------|
| catalog.batchInsertObjects | Create items | 3 |
| catalog.batchUpdateObjects | Update SEO | 3 |
| catalog.batchGetObjects | Retrieve items | 3 |
| inventory.batchChange | Set inventory | 3 |
| checkout.createPaymentLink | Generate payment links | 5 |
| checkout.listPaymentLinks | List existing links | 5 |

### Location & Category IDs

| Entity | ID | Notes |
|--------|-----|-------|
| Richmond General Location | B87BAEZ0NWV34 | Primary location |
| Timeless Treasures | 3N3II4W6Q7AA43RWQGEEWELY | Main category |
| The New Finds | P34KX3L7XRZJJ5RP6W35K4YO | REQUIRED for new items |

## 5.2 Payment Link Creation

### Request Structure
```python
{
    "idempotency_key": "unique-uuid",
    "order": {
        "location_id": "B87BAEZ0NWV34",
        "line_items": [{
            "catalog_object_id": "VARIATION_ID",  # NOT item_id!
            "quantity": "1"
        }]
    },
    "checkout_options": {
        "ask_for_shipping_address": True,  # If shippable
        "accepted_payment_methods": {
            "apple_pay": True,
            "google_pay": True,
            "cash_app_pay": True
        }
    }
}
```

### Response Structure
```python
{
    "payment_link": {
        "id": "LINK_ID",
        "url": "https://square.link/u/XXXXXXX",  # USE THIS FOR QR
        "long_url": "https://checkout.square.site/...",
        "order_id": "ORDER_ID",
        "version": 1
    }
}
```

## 5.3 Catalog Item Creation

### Request Structure
```python
{
    "objects": [{
        "type": "ITEM",
        "id": "#temp-id",
        "present_at_all_locations": False,
        "present_at_location_ids": ["B87BAEZ0NWV34"],
        "item_data": {
            "name": "Item Name",
            "description": "Full description",
            "category_ids": [
                "3N3II4W6Q7AA43RWQGEEWELY",
                "P34KX3L7XRZJJ5RP6W35K4YO"
            ],
            "variations": [{
                "type": "ITEM_VARIATION",
                "id": "#temp-var",
                "item_variation_data": {
                    "name": "Regular",
                    "sku": "RG-XXXX",
                    "pricing_type": "FIXED_PRICING",
                    "price_money": {
                        "amount": 1999,
                        "currency": "USD"
                    },
                    "track_inventory": True,
                    "sellable": True,
                    "stockable": True
                }
            }],
            "ecom_visibility": "VISIBLE",
            "is_taxable": True
        }
    }]
}
```

## 5.4 SEO Update

### Request Structure
```python
{
    "objects": [{
        "type": "ITEM",
        "id": "ACTUAL_ITEM_ID",
        "version": CURRENT_VERSION,  # REQUIRED
        "item_data": {
            "ecom_seo_data": {
                "permalink": "slug",
                "page_title": "Title",
                "page_description": "Description"
            }
        }
    }],
    "sparse_update": True  # REQUIRED
}
```

## 5.5 Inventory Update

### Request Structure
```python
{
    "changes": [{
        "type": "ADJUSTMENT",
        "adjustment": {
            "from_state": "NONE",
            "to_state": "IN_STOCK",
            "location_id": "B87BAEZ0NWV34",
            "catalog_object_id": "VARIATION_ID",
            "quantity": "1",
            "occurred_at": "ISO_TIMESTAMP"
        }
    }]
}
```

---

# 6. Business Logic

## 6.1 Shipping Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                  SHIPPING DECISION TREE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Is item fragile AND large?                                  │
│  ├── YES ──▶ PICKUP ONLY                                     │
│  └── NO                                                      │
│       │                                                      │
│       ▼                                                      │
│  Is item > 10 lbs?                                           │
│  ├── YES ──▶ PICKUP ONLY                                     │
│  └── NO                                                      │
│       │                                                      │
│       ▼                                                      │
│  Does item require custom crating?                           │
│  ├── YES ──▶ PICKUP ONLY                                     │
│  └── NO                                                      │
│       │                                                      │
│       ▼                                                      │
│  SHIPPABLE ──▶ Enable all fulfillment methods                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Shippable Items (Enable All Methods)
- Books, pamphlets, paper goods
- Small glassware (properly packed)
- Small pottery/ceramics
- Jewelry, small collectibles
- Textiles, linens

### Pickup Only Items
- Large furniture
- Large/fragile glass pieces
- Heavy pottery/stoneware
- Framed art/mirrors
- Chandeliers, lamps
- Anything requiring custom crating

## 6.2 Pricing Formula

```
1. Research comps (eBay sold, AbeBooks, LiveAuctioneers)
2. Find low-end retail price
3. Apply condition adjustment:
   - Mint/Excellent: 100%
   - Very Good: 70-85%
   - Good: 50-70%
   - Fair: 20-40%
4. Target 60-80% of adjusted retail
5. Round to price ladder
6. Verify margin ≥ minimum (usually 1.5-2x cost)
```

### Price Ladder
```
Under $10:  $3.99, $4.99, $5.99, $7.99, $9.99
$10-$25:    $12.99, $14.99, $17.99, $19.99, $22.99, $24.99
$25-$50:    $27.99, $29.99, $34.99, $39.99, $44.99, $49.99
$50-$100:   $54.99, $59.99, $69.99, $79.99, $89.99, $99.99
$100+:      Round to nearest $10 or $25
```

## 6.3 Condition Grading

### Books (Antiquarian Scale)
| Grade | Criteria |
|-------|----------|
| Fine (F) | Near perfect, minimal signs of age |
| Very Good (VG) | Minor wear, tight binding, clean pages |
| Good (G) | Obvious wear, all pages present, readable |
| Fair | Heavy wear, possible damage, complete |
| Poor | Major damage, for reading only |

### Glass/Pottery
| Grade | Criteria |
|-------|----------|
| Mint | Perfect, no flaws |
| Excellent | Minimal wear, no damage |
| Very Good | Light wear, no chips/cracks |
| Good | Moderate wear, minor flaws |
| Fair | Chips, cracks, or repairs present |

## 6.4 SEO Templates

### Permalink Format
```
{key-terms}-{era/date}-{type}
```
Examples:
- `orphan-annie-1931-comic-strips-dover`
- `northwood-grape-cable-bowl-amethyst`

### Page Title Format (50-60 chars)
```
{Item Name} | {Era/Style} {Type}
```
Examples:
- `Little Orphan Annie 1931 Comic Strips | Vintage Dover Reprint`
- `Northwood Grape & Cable Bowl | Antique Carnival Glass`

### Page Description (150-160 chars)
Include:
- Key item details
- Era/date
- Condition highlight
- Call to action

---

# 7. File Organization

## 7.1 Directory Structure

```
/items/                              # Root for all inventory items
├── RG-0001/                         # Item folder (by SKU)
│   ├── images/                      # All product images
│   │   ├── RG-0001-main.jpg        # Primary photo
│   │   ├── RG-0001-back.jpg        # Additional angles
│   │   ├── RG-0001-mark.jpg        # Maker's mark detail
│   │   └── RG-0001-nobg.png        # Background removed
│   ├── qr/                          # QR code assets
│   │   └── RG-0001-payment-qr.png  # Payment link QR
│   ├── label/                       # Label files
│   │   └── RG-0001-label.csv       # Print Master data
│   ├── info-card/                   # Info card for GitHub Pages
│   │   └── index.html              # Flip card HTML (museum placard)
│   └── metadata.json                # Complete item record
├── RG-0002/
│   └── ...
├── _archive/                        # Sold/removed items
│   └── RG-0001/                     # Moved after sale
└── template/                        # Shared templates
    └── rg-item-card-template.html  # Master info card template
```

**GitHub Pages Repository Structure:**
```
richmondgeneral/items/               # GitHub org/repo
├── index.html                       # Item gallery/index (optional)
├── RG-0001/
│   └── index.html                  # → richmondgeneral.github.io/items/RG-0001/
├── RG-0002/
│   └── index.html
└── assets/
    ├── styles.css                  # Shared styles (optional)
    └── rg-logo.png                 # Brand assets
```

## 7.2 File Naming Convention

```
{SKU}-{descriptor}.{ext}
```

| File Type | Pattern | Example |
|-----------|---------|---------|
| Main image | SKU-main.jpg | RG-0001-main.jpg |
| Additional image | SKU-{view}.jpg | RG-0001-back.jpg |
| Background removed | SKU-nobg.png | RG-0001-nobg.png |
| QR code | SKU-payment-qr.png | RG-0001-payment-qr.png |
| Label CSV | SKU-label.csv | RG-0001-label.csv |
| Info card | index.html | info-card/index.html |
| Metadata | metadata.json | metadata.json |

---

# 8. Verification Checklist

## 8.1 Skill Installation Check

Run this checklist to verify all skills are properly installed:

### rg-inventory Skill
- [ ] SKILL.md exists and has YAML frontmatter
- [ ] references/pricing-guidelines.md exists
- [ ] references/lot-tracking.md exists
- [ ] references/square-catalog.md exists
- [ ] references/label-format.md exists
- [ ] Contains specialist routing rules
- [ ] Contains shipping decision logic
- [ ] Contains payment link workflow

### vintage-appraiser Skill
- [ ] SKILL.md exists and has YAML frontmatter
- [ ] Contains book-appraiser routing
- [ ] references/research-sources.md exists
- [ ] references/carnival-glass.md exists
- [ ] references/pricing-research.md exists
- [ ] references/listing-descriptions.md exists
- [ ] Contains maker's mark identification workflow
- [ ] Contains dating clues reference table

### book-appraiser Skill
- [ ] SKILL.md exists and has YAML frontmatter
- [ ] references/condition-grading.md exists
- [ ] Contains edition identification workflow
- [ ] Contains Library of Congress integration notes
- [ ] Contains Richmond General pricing application

### product-labeler Skill
- [ ] SKILL.md exists
- [ ] Contains Print Master CSV format
- [ ] Contains style guide reference

## 8.2 Item Processing Verification

For each item, verify:

### Catalog Entry
- [ ] Item ID assigned
- [ ] Variation ID assigned
- [ ] SKU set (RG-XXXX format)
- [ ] Price set correctly
- [ ] Categories assigned (both Timeless Treasures AND The New Finds)
- [ ] Description complete
- [ ] Image uploaded
- [ ] Inventory count set to 1
- [ ] SEO configured (permalink, title, description)

### Fulfillment
- [ ] Shippability assessed
- [ ] If shippable: Shipping box assigned
- [ ] Fulfillment methods enabled appropriately

### Payment Link
- [ ] Payment link created
- [ ] Link URL captured (square.link/u/...)
- [ ] QR code generated from payment link
- [ ] QR PNG saved to item folder

### Files
- [ ] Item folder created (/items/RG-XXXX/)
- [ ] Images stored in images/ subfolder
- [ ] QR code stored in qr/ subfolder
- [ ] metadata.json created with all IDs and URLs
- [ ] Label CSV created if needed

### Info Card (Phase 7)
- [ ] index.html created from template
- [ ] Story/provenance text written
- [ ] All placeholder variables replaced
- [ ] Actual QR code image embedded (or SVG placeholder updated)
- [ ] Payment link URL updated in buy button
- [ ] Deployed to GitHub Pages
- [ ] Live URL accessible: richmondgeneral.github.io/items/RG-XXXX/
- [ ] Flip interaction works on mobile and desktop
- [ ] Print version renders correctly (if printing cards)

## 8.3 API Integration Check

Verify these integrations work:

- [ ] catalog.batchInsertObjects creates items
- [ ] catalog.batchUpdateObjects updates SEO (with version + sparse_update)
- [ ] inventory.batchChange sets inventory
- [ ] checkout.createPaymentLink generates links
- [ ] Can retrieve item by ID
- [ ] Can retrieve payment link by ID

## 8.4 Quick Functionality Test

Create a test item and verify:

1. [ ] Can route to vintage-appraiser for glass/pottery
2. [ ] Can route to book-appraiser for books
3. [ ] Can create Square catalog item
4. [ ] Can set inventory
5. [ ] Can configure SEO
6. [ ] Can create payment link
7. [ ] Can generate QR code
8. [ ] Can create item folder structure
9. [ ] Can generate label CSV
10. [ ] Can generate info card HTML from template
11. [ ] Can deploy info card to GitHub Pages

---

# Appendix: Reference Data

## A.1 Square IDs

| Entity | ID |
|--------|-----|
| Richmond General Location | B87BAEZ0NWV34 |
| Timeless Treasures Category | 3N3II4W6Q7AA43RWQGEEWELY |
| The New Finds Category | P34KX3L7XRZJJ5RP6W35K4YO |

## A.2 Square Sites

| Site | Domain | Site ID |
|------|--------|---------|
| Richmond General | www.richmondgeneral.com | site_649797114786509406 |
| TVM | www.tresorvintagemarket.com | site_915778696556732343 |
| DRZB Patikas | www.drzbpatikus.com | site_941347487482744550 |
| TBDLabz | www.tbdlabz.shop | site_139774427146032794 |
| Richmond Vintage Market | www.richmondvintagemarket.com | site_263989558375536490 |

## A.3 URL Formats

| URL Type | Format | Use For |
|----------|--------|---------|
| Payment Link | https://square.link/u/XXXXXXX | QR codes on labels |
| Product Page | https://www.richmondgeneral.com/product/{permalink}/{item_id} | Direct linking |

## A.4 Completed Items

| SKU | Item | Price | Item ID | Variation ID | Payment Link | Status |
|-----|------|-------|---------|--------------|--------------|--------|
| RG-0001 | 1979 Little Orphan Annie Comic Strip Book | $19.99 | 2A2VL6JA6VHOQLRLERFR5BZJ | UQORP6UPBOGGNDKOE4GU2M2J | PENDING | Catalog created |

## A.5 Active Purchase Lots

| Lot ID | Description | Date | Cost | Status |
|--------|-------------|------|------|--------|
| PETER-002 | Peter Visit 2 | Nov 19, 2025 | $200 | Processing |
| IOWA-0925 | Iowa Auction (94 lots) | Sept 2025 | $771.09 | Processing |

---

# Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 26, 2025 | Initial release - complete system documentation |

---

*This document serves as the single source of truth for the Richmond General Inventory System. If any skill or functionality appears missing, reference this document to identify and restore it.*
