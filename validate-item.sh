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

# Check for SVG QR codes (should be PNG only)
if [ -f "$ITEM_FOLDER/qr-code.svg" ]; then
    echo "${YELLOW}⚠${NC} qr-code.svg found (should use PNG only)"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

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
        echo "${GREEN}✓${NC} Square payment link present"
    else
        echo "${RED}✗${NC} Square payment link missing"
        ERRORS=$((ERRORS + 1))
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
