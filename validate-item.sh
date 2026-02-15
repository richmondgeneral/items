#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if item folder provided
if [ -z "$1" ]; then
    echo "${RED}Usage: $0 <item-folder>${NC}"
    echo "Example: $0 RG-0007"
    exit 1
fi

ITEM_FOLDER=$1

if [ ! -d "$ITEM_FOLDER" ]; then
    echo "${RED}Error: Folder $ITEM_FOLDER does not exist${NC}"
    exit 1
fi

echo "=========================================="
echo "Validating: $ITEM_FOLDER"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0
ITEM_STATUS="available"

if [ -f "$ITEM_FOLDER/status.json" ] && grep -q '"status"[[:space:]]*:[[:space:]]*"sold"' "$ITEM_FOLDER/status.json"; then
    ITEM_STATUS="sold"
fi

echo "Item Status: $ITEM_STATUS"
echo ""

# Check required files
echo "Required Files:"

if [ -f "$ITEM_FOLDER/index.html" ]; then
    echo "${GREEN}✓${NC} index.html"
else
    echo "${RED}✗${NC} index.html MISSING"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$ITEM_FOLDER/hero.jpeg" ] || [ -f "$ITEM_FOLDER/hero.png" ]; then
    echo "${GREEN}✓${NC} hero image"
else
    echo "${RED}✗${NC} hero.{jpeg|png} MISSING"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$ITEM_FOLDER/qr-code.png" ]; then
    echo "${GREEN}✓${NC} qr-code.png"
else
    echo "${RED}✗${NC} qr-code.png MISSING"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$ITEM_FOLDER/label.json" ]; then
    echo "${GREEN}✓${NC} label.json"
else
    echo "${RED}✗${NC} label.json MISSING"
    ERRORS=$((ERRORS + 1))
fi

# Check for SVG QR codes (should be PNG only)
if [ -f "$ITEM_FOLDER/qr-code.svg" ]; then
    echo "${YELLOW}⚠${NC} qr-code.svg found (should use PNG only)"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Validate label metadata
if [ -f "$ITEM_FOLDER/label.json" ]; then
    echo "Label Metadata:"
    LABEL_CHECK_OUTPUT=$(python3 - "$ITEM_FOLDER" <<'PY'
import json
import re
import sys
from pathlib import Path

item_folder = Path(sys.argv[1])
sku = item_folder.name
path = item_folder / "label.json"

required = [
    "sku",
    "product_name",
    "attributes",
    "price",
    "condition",
    "condition_notes",
    "qr_code_url",
]

payload = json.loads(path.read_text(encoding="utf-8"))
if not isinstance(payload, dict):
    raise ValueError("label.json root must be an object")

missing = [key for key in required if key not in payload]
if missing:
    raise ValueError(f"missing field(s): {', '.join(missing)}")

if payload.get("sku") != sku:
    raise ValueError(f"sku field ({payload.get('sku')}) does not match folder ({sku})")

if not re.fullmatch(r"RG-\d{4}", str(payload.get("sku", ""))):
    raise ValueError("sku must match RG-XXXX")

price_raw = str(payload.get("price", "")).replace("$", "").strip()
float(price_raw)

qr_url = str(payload.get("qr_code_url", "")).strip()
if not qr_url.startswith("http://") and not qr_url.startswith("https://"):
    raise ValueError("qr_code_url must be an absolute URL")

for key in ("product_name", "attributes", "condition"):
    if not str(payload.get(key, "")).strip():
        raise ValueError(f"{key} must not be empty")

print("ok")
PY
)
    LABEL_CHECK_STATUS=$?
    if [ $LABEL_CHECK_STATUS -eq 0 ]; then
        echo "${GREEN}✓${NC} label.json schema valid"
    else
        echo "${RED}✗${NC} label.json invalid: $LABEL_CHECK_OUTPUT"
        ERRORS=$((ERRORS + 1))
    fi
    echo ""
fi

# Check for unreplaced placeholders
if [ -f "$ITEM_FOLDER/index.html" ]; then
    echo "Placeholder Check:"
    
    PLACEHOLDERS=$(grep -o "{{[A-Z_]*}}" "$ITEM_FOLDER/index.html" | sort -u)
    
    if [ -z "$PLACEHOLDERS" ]; then
        echo "${GREEN}✓${NC} No unreplaced placeholders"
    else
        echo "${RED}✗${NC} Found unreplaced placeholders:"
        echo "$PLACEHOLDERS" | while read -r placeholder; do
            echo "   - $placeholder"
        done
        ERRORS=$((ERRORS + 1))
    fi
    
    echo ""
fi

# Check working images
echo "Working Images:"
SKU=$(basename "$ITEM_FOLDER")

if [ -f "assets/working-images/$SKU-hero.jpeg" ] || [ -f "assets/working-images/$SKU-hero.png" ]; then
    echo "${GREEN}✓${NC} Original hero image in working-images"
else
    echo "${YELLOW}⚠${NC} No original hero image found in assets/working-images/"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Check HTML content
if [ -f "$ITEM_FOLDER/index.html" ]; then
    echo "Content Check:"
    
    if grep -q "square.link" "$ITEM_FOLDER/index.html"; then
        if [ "$ITEM_STATUS" = "sold" ]; then
            echo "${YELLOW}⚠${NC} Square payment link present on sold archive item (consider removing checkout)"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "${GREEN}✓${NC} Square payment link present"
        fi
    else
        if [ "$ITEM_STATUS" = "sold" ]; then
            echo "${GREEN}✓${NC} Sold archive item intentionally has no Square payment link"
        else
            echo "${RED}✗${NC} Square payment link missing"
            ERRORS=$((ERRORS + 1))
        fi
    fi
    
    if grep -q "flip-card" "$ITEM_FOLDER/index.html"; then
        echo "${GREEN}✓${NC} Flip card UI present"
    else
        echo "${YELLOW}⚠${NC} Flip card UI missing"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if grep -q "aria-" "$ITEM_FOLDER/index.html"; then
        echo "${GREEN}✓${NC} Accessibility (ARIA) labels present"
    else
        echo "${YELLOW}⚠${NC} ARIA labels missing (accessibility)"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if grep -q "@media print" "$ITEM_FOLDER/index.html"; then
        echo "${GREEN}✓${NC} Print styles present"
    else
        echo "${YELLOW}⚠${NC} Print styles missing"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    echo ""
fi

# Check file sizes
echo "File Sizes:"

if [ -f "$ITEM_FOLDER/hero.jpeg" ]; then
    SIZE=$(stat -f%z "$ITEM_FOLDER/hero.jpeg" 2>/dev/null || stat -c%s "$ITEM_FOLDER/hero.jpeg")
    SIZE_MB=$(echo "scale=2; $SIZE / 1048576" | bc)
    if (( $(echo "$SIZE_MB > 1.0" | bc -l) )); then
        echo "${YELLOW}⚠${NC} hero.jpeg is ${SIZE_MB}MB (recommend < 1MB)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "${GREEN}✓${NC} hero.jpeg size OK (${SIZE_MB}MB)"
    fi
fi

if [ -f "$ITEM_FOLDER/hero.png" ]; then
    SIZE=$(stat -f%z "$ITEM_FOLDER/hero.png" 2>/dev/null || stat -c%s "$ITEM_FOLDER/hero.png")
    SIZE_MB=$(echo "scale=2; $SIZE / 1048576" | bc)
    if (( $(echo "$SIZE_MB > 1.0" | bc -l) )); then
        echo "${YELLOW}⚠${NC} hero.png is ${SIZE_MB}MB (recommend < 1MB)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "${GREEN}✓${NC} hero.png size OK (${SIZE_MB}MB)"
    fi
fi

echo ""

# Summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "${GREEN}✓ Validation passed!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo "${YELLOW}$WARNINGS warning(s) - review recommended${NC}"
    fi
    echo ""
    echo "Ready to deploy:"
    echo "  ${GREEN}git add $ITEM_FOLDER${NC}"
    echo "  ${GREEN}git commit -m \"Add $SKU: [Item Name]\"${NC}"
    echo "  ${GREEN}git push origin main${NC}"
    exit 0
else
    echo "${RED}✗ Validation failed with $ERRORS error(s)${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo "${YELLOW}$WARNINGS warning(s)${NC}"
    fi
    echo ""
    echo "Fix the errors above before deploying."
    exit 1
fi
