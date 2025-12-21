#!/bin/bash
# Test that critical CSS properties are present

ITEM=$1

if [ -z "$ITEM" ]; then
    echo "Usage: ./test-css-requirements.sh RG-XXXX"
    exit 1
fi

if [ ! -d "$ITEM" ]; then
    echo "❌ FAIL: Item folder $ITEM does not exist"
    exit 1
fi

if [ ! -f "$ITEM/index.html" ]; then
    echo "❌ FAIL: $ITEM/index.html does not exist"
    exit 1
fi

echo "Testing $ITEM CSS requirements..."

# Check for min-height: 0 on image container
if ! grep -q "min-height: 0" "$ITEM/index.html"; then
    echo "❌ FAIL: Missing 'min-height: 0' on .item-image-container"
    exit 1
fi
echo "✅ PASS: min-height: 0 present"

# Check for flex-shrink: 0 on footer
if ! grep -q "flex-shrink: 0" "$ITEM/index.html"; then
    echo "❌ FAIL: Missing 'flex-shrink: 0' on footer"
    exit 1
fi
echo "✅ PASS: flex-shrink: 0 present"

# Check for aspect-ratio
if ! grep -q "aspect-ratio: 5 / 7" "$ITEM/index.html"; then
    echo "❌ FAIL: Missing 'aspect-ratio: 5 / 7'"
    exit 1
fi
echo "✅ PASS: aspect-ratio: 5 / 7 present"

# Check for proper flip card classes
if ! grep -q 'class="flip-card"' "$ITEM/index.html"; then
    echo "❌ FAIL: Missing flip-card class"
    exit 1
fi
echo "✅ PASS: flip-card class present"

# Check for card-face classes
if ! grep -q 'class="card-face card-front"' "$ITEM/index.html"; then
    echo "❌ FAIL: Missing card-face card-front classes"
    exit 1
fi
echo "✅ PASS: card-face card-front present"

if ! grep -q 'class="card-face card-back"' "$ITEM/index.html"; then
    echo "❌ FAIL: Missing card-face card-back classes"
    exit 1
fi
echo "✅ PASS: card-face card-back present"

echo "✅ All CSS requirements met for $ITEM"
