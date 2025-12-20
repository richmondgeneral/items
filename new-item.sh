#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Richmond General - New Item Setup"
echo "=========================================="
echo ""

# Function to get next SKU number
get_next_sku() {
    local max_num=0
    for dir in RG-*/; do
        if [ -d "$dir" ]; then
            num=$(echo "$dir" | sed 's/RG-0*\([0-9]*\)\//\1/')
            if [ "$num" -gt "$max_num" ]; then
                max_num=$num
            fi
        fi
    done
    echo $((max_num + 1))
}

# Get SKU
NEXT_NUM=$(get_next_sku)
printf "${BLUE}Enter SKU number (press Enter for RG-%04d):${NC} " "$NEXT_NUM"
read SKU_INPUT

if [ -z "$SKU_INPUT" ]; then
    SKU_NUM=$NEXT_NUM
else
    SKU_NUM=$SKU_INPUT
fi

SKU=$(printf "RG-%04d" "$SKU_NUM")
FOLDER=$SKU

# Check if folder already exists
if [ -d "$FOLDER" ]; then
    echo "${RED}Error: Folder $FOLDER already exists${NC}"
    exit 1
fi

echo ""
echo "${GREEN}Creating new item: $SKU${NC}"
echo ""

# Gather item information
printf "${BLUE}Item title:${NC} "
read ITEM_TITLE

printf "${BLUE}Era line (e.g., '1930s Americana'):${NC} "
read ERA_LINE

printf "${BLUE}Price (e.g., 19.99):${NC} "
read PRICE

printf "${BLUE}Era (for details grid, e.g., '1930s'):${NC} "
read ERA

printf "${BLUE}Condition (e.g., 'Very Good'):${NC} "
read CONDITION

printf "${BLUE}Maker/Publisher:${NC} "
read MAKER

printf "${BLUE}Origin (e.g., 'USA'):${NC} "
read ORIGIN

printf "${BLUE}Square payment link (square.link/u/...):${NC} "
read PAYMENT_LINK

echo ""
printf "${BLUE}Item story/provenance (press Enter when done, Ctrl+D on empty line):${NC}\n"
STORY_TEXT=$(cat)

printf "${BLUE}SEO description (150-160 chars):${NC} "
read SEO_DESCRIPTION

# Create folder
echo ""
echo "${YELLOW}Creating folder: $FOLDER${NC}"
mkdir -p "$FOLDER"

# Copy and process template
echo "${YELLOW}Generating index.html from template...${NC}"
cp template/rg-item-card-template.html "$FOLDER/index.html"

# Replace placeholders
sed -i '' "s|{{SKU}}|$SKU|g" "$FOLDER/index.html"
sed -i '' "s|{{ITEM_TITLE}}|$ITEM_TITLE|g" "$FOLDER/index.html"
sed -i '' "s|{{ERA_LINE}}|$ERA_LINE|g" "$FOLDER/index.html"
sed -i '' "s|{{PRICE}}|$PRICE|g" "$FOLDER/index.html"
sed -i '' "s|{{ERA}}|$ERA|g" "$FOLDER/index.html"
sed -i '' "s|{{CONDITION}}|$CONDITION|g" "$FOLDER/index.html"
sed -i '' "s|{{MAKER}}|$MAKER|g" "$FOLDER/index.html"
sed -i '' "s|{{ORIGIN}}|$ORIGIN|g" "$FOLDER/index.html"
sed -i '' "s|{{IMAGE_URL}}|./hero.jpeg|g" "$FOLDER/index.html"
sed -i '' "s|{{QR_CODE_URL}}|./qr-code.png|g" "$FOLDER/index.html"
sed -i '' "s|{{PAYMENT_LINK_URL}}|$PAYMENT_LINK|g" "$FOLDER/index.html"
sed -i '' "s|{{SEO_DESCRIPTION}}|$SEO_DESCRIPTION|g" "$FOLDER/index.html"

# Handle story text (escape for sed)
STORY_ESCAPED=$(echo "$STORY_TEXT" | sed 's/[\/&]/\\&/g' | sed ':a;N;$!ba;s/\n/\\n/g')
sed -i '' "s|{{STORY_TEXT}}|$STORY_ESCAPED|g" "$FOLDER/index.html"

echo "${GREEN}✓ index.html created${NC}"

# Next steps
echo ""
echo "=========================================="
echo "${GREEN}Item folder created: $FOLDER${NC}"
echo "=========================================="
echo ""
echo "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Add item image:"
echo "   ${BLUE}cp [source-image] assets/working-images/$SKU-hero.jpeg${NC}"
echo ""
echo "2. Process image with square-image-upload skill:"
echo "   - Removes background"
echo "   - Uploads to Square catalog"
echo "   - Creates $SKU-hero-converted.jpeg in root"
echo ""
echo "3. Move processed image to item folder:"
echo "   ${BLUE}mv $SKU-hero-converted.jpeg $FOLDER/hero.jpeg${NC}"
echo ""
echo "4. Generate QR code from Square payment link:"
echo "   - Visit: $PAYMENT_LINK"
echo "   - Generate QR code (300x300px recommended)"
echo "   - Save as: ${BLUE}$FOLDER/qr-code.png${NC}"
echo ""
echo "5. Validate before deploying:"
echo "   ${BLUE}./validate-item.sh $FOLDER${NC}"
echo ""
echo "6. Deploy to GitHub Pages:"
echo "   ${BLUE}git add $FOLDER${NC}"
echo "   ${BLUE}git commit -m \"Add $SKU: $ITEM_TITLE\"${NC}"
echo "   ${BLUE}git push origin main${NC}"
echo ""
echo "Live URL will be:"
echo "${GREEN}https://richmondgeneral.github.io/items/$SKU/${NC}"
echo ""
