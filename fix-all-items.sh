#!/bin/bash
# Batch apply CSS fixes to all items that need them

echo "Checking all items and applying fixes..."

for item in RG-000{1..9}; do
    if [ ! -d "$item" ] || [ ! -f "$item/index.html" ]; then
        continue
    fi
    
    echo ""
    echo "Processing $item..."
    
    NEEDS_FIX=false
    
    # Check for min-height: 0
    if ! grep -q "min-height: 0" "$item/index.html"; then
        echo "  ⚠️  Missing min-height: 0"
        NEEDS_FIX=true
        
        # Add min-height: 0 after flex: 1 1 0 in .item-image-container
        sed -i.bak 's/\(\.item-image-container {\)/\1\n            min-height: 0;/' "$item/index.html"
        
        # If that didn't work, try after "flex: 1;"
        if ! grep -q "min-height: 0" "$item/index.html"; then
            sed -i.bak '/\.item-image-container {/,/}/ s/\(flex: 1;\)/\1\n            min-height: 0;/' "$item/index.html"
        fi
    fi
    
    # Check for flex: 1 1 0 (should be instead of just flex: 1)
    if grep -A 1 "\.item-image-container {" "$item/index.html" | grep -q "flex: 1;$" && ! grep -q "flex: 1 1 0;" "$item/index.html"; then
        echo "  ⚠️  Wrong flex value on image container"
        NEEDS_FIX=true
        sed -i.bak '/\.item-image-container {/,/}/ s/flex: 1;/flex: 1 1 0;/' "$item/index.html"
    fi
    
    # Check for flex-shrink: 0 on footers
    if ! grep -q "flex-shrink: 0" "$item/index.html"; then
        echo "  ⚠️  Missing flex-shrink: 0 on footer"
        NEEDS_FIX=true
        
        # Add to .front-footer
        sed -i.bak '/\.front-footer {/,/}/ s/\(\.front-footer {\)/\1\n            flex-shrink: 0;\n            height: 44px;/' "$item/index.html"
        
        # Add to .back-footer
        sed -i.bak '/\.back-footer {/,/}/ s/\(\.back-footer {\)/\1\n            flex-shrink: 0;\n            height: 80px;/' "$item/index.html"
    fi
    
    # Check for flex: 0 0 auto on .front-info (not flex: 1)
    if grep -A 1 "\.front-info {" "$item/index.html" | grep -q "flex: 1;$" && ! grep -q "flex: 0 0 auto;" "$item/index.html"; then
        echo "  ⚠️  Wrong flex value on front-info (should be 0 0 auto, not 1)"
        NEEDS_FIX=true
        sed -i.bak '/\.front-info {/,/}/ s/flex: 1;/flex: 0 0 auto;/' "$item/index.html"
    fi
    
    if [ "$NEEDS_FIX" = true ]; then
        echo "  ✅ Applied fixes to $item"
        rm -f "$item/index.html.bak"
    else
        echo "  ✅ $item already has all fixes"
    fi
done

echo ""
echo "✅ Batch fix complete!"
echo ""
echo "Run validation:"
echo "  ./test-css-requirements.sh RG-0001"
echo "  ./test-css-requirements.sh RG-0007"
echo ""
echo "Test locally:"
echo "  python3 -m http.server 8000"
