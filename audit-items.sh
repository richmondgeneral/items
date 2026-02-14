#!/bin/bash

echo "=========================================="
echo "Richmond General Item Audit"
echo "=========================================="
echo ""

for dir in RG-*; do
    if [ ! -d "$dir" ]; then
        continue
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 $dir"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check for required files
    echo "Files:"
    if [ -f "$dir/index.html" ]; then
        echo "  ✅ index.html"
    else
        echo "  ❌ index.html MISSING"
    fi
    
    if [ -f "$dir/hero.jpeg" ] || [ -f "$dir/hero.jpg" ] || [ -f "$dir/hero.png" ]; then
        echo "  ✅ hero image"
    else
        echo "  ❌ hero image MISSING"
    fi
    
    if [ -f "$dir/qr-code.png" ]; then
        echo "  ✅ qr-code.png"
    else
        echo "  ❌ qr-code.png MISSING"
    fi

    if [ -f "$dir/label.json" ]; then
        echo "  ✅ label.json"
    else
        echo "  ❌ label.json MISSING"
    fi
    
    # Check index.html content
    if [ -f "$dir/index.html" ]; then
        echo ""
        echo "Design Elements:"
        
        # Check for brand colors
        if grep -q "rg-gold" "$dir/index.html"; then
            echo "  ✅ Brand colors (CSS variables)"
        else
            echo "  ❌ Brand colors missing"
        fi
        
        # Check for flip card
        if grep -q "flip-card" "$dir/index.html"; then
            echo "  ✅ Flip card UI"
        else
            echo "  ❌ Flip card UI missing"
        fi
        
        # Check for fonts
        if grep -q "Playfair Display" "$dir/index.html"; then
            echo "  ✅ Playfair Display font"
        else
            echo "  ❌ Playfair Display font missing"
        fi
        
        if grep -q "Source Sans Pro" "$dir/index.html"; then
            echo "  ✅ Source Sans Pro font"
        else
            echo "  ❌ Source Sans Pro font missing"
        fi
        
        # Check for SKU badge
        if grep -q "sku-badge\|SKU" "$dir/index.html"; then
            echo "  ✅ SKU badge"
        else
            echo "  ❌ SKU badge missing"
        fi
        
        # Check for price
        if grep -q "item-price\|price" "$dir/index.html"; then
            echo "  ✅ Price display"
        else
            echo "  ❌ Price display missing"
        fi
        
        # Check for story section
        if grep -q "story-section\|story" "$dir/index.html"; then
            echo "  ✅ Story/provenance"
        else
            echo "  ❌ Story/provenance missing"
        fi
        
        # Check for details grid
        if grep -q "details-grid\|detail-item" "$dir/index.html"; then
            echo "  ✅ Details grid"
        else
            echo "  ❌ Details grid missing"
        fi
        
        # Check for Square payment link
        if grep -q "square.link" "$dir/index.html"; then
            LINK=$(grep -o "square.link/u/[A-Za-z0-9]*" "$dir/index.html" | head -1)
            echo "  ✅ Square payment link ($LINK)"
        else
            echo "  ❌ Square payment link MISSING"
        fi
        
        # Check for Buy Now button
        if grep -q "buy-button\|Buy Now" "$dir/index.html"; then
            echo "  ✅ Buy Now button"
        else
            echo "  ❌ Buy Now button missing"
        fi
        
        # Check for QR code reference
        if grep -q "qr-code" "$dir/index.html"; then
            echo "  ✅ QR code reference"
        else
            echo "  ❌ QR code reference missing"
        fi
        
        # Check for accessibility features
        echo ""
        echo "Accessibility:"
        if grep -q "aria-" "$dir/index.html"; then
            echo "  ✅ ARIA labels"
        else
            echo "  ❌ ARIA labels missing"
        fi
        
        if grep -q "tabindex" "$dir/index.html"; then
            echo "  ✅ Keyboard navigation"
        else
            echo "  ❌ Keyboard navigation missing"
        fi
        
        # Check for print styles
        if grep -q "@media print" "$dir/index.html"; then
            echo "  ✅ Print styles"
        else
            echo "  ❌ Print styles missing"
        fi
        
        # Check for brand strip/footer
        if grep -q "richmondgeneral.com\|Richmond General" "$dir/index.html"; then
            echo "  ✅ Brand footer"
        else
            echo "  ❌ Brand footer missing"
        fi
    fi
    
    echo ""
done

echo "=========================================="
echo "Audit Complete"
echo "=========================================="
