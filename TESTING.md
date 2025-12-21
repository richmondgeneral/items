# Testing Guide for Richmond General Item Cards

## Local Testing (Before Deploy)

### 1. Simple HTTP Server

Start a local server to preview cards:

```bash
# Python 3 (built-in)
python3 -m http.server 8000

# Or using Node.js
npx serve .

# Or using PHP
php -S localhost:8000
```

Then visit:
- http://localhost:8000/RG-0001/
- http://localhost:8000/RG-0008/

### 2. Browser DevTools Testing

Open DevTools (F12) and test:

**Responsive Design Mode:**
```
- Desktop: 1920×1080, 1440×900
- Tablet: 768×1024 (iPad)
- Mobile: 375×667 (iPhone SE), 390×844 (iPhone 13)
```

**Network Throttling:**
- Fast 3G (simulate mobile)
- Slow 3G (worst case)

**Accessibility:**
- Screen reader mode (VoiceOver on Mac, NVDA on Windows)
- Keyboard navigation only (Tab, Enter, Space)
- Contrast checker

### 3. Visual Regression Testing

#### Manual Checklist
```bash
# For each item (RG-0001, RG-0008, etc.):

□ Card height: ~588px at max-width (420px)
□ SKU badge visible in top-right
□ Image fills container, properly centered
□ Title fully visible
□ Era line fully visible
□ Price fully visible
□ "Tap for story" hint visible
□ No content cut off at bottom
□ Flip animation smooth
□ Back side fully visible
□ Footer aligned on front and back
```

#### Automated Screenshot Comparison
```bash
# Install Playwright for screenshot testing
npm install -D @playwright/test

# See test-visual-regression.js below
npx playwright test
```

## Automated Validation Scripts

### CSS Validation Script

Create `test-css-requirements.sh`:

```bash
#!/bin/bash
# Test that critical CSS properties are present

ITEM=$1

if [ -z "$ITEM" ]; then
    echo "Usage: ./test-css-requirements.sh RG-XXXX"
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

echo "✅ All CSS requirements met"
```

### Playwright Visual Regression Test

Create `test-visual-regression.js`:

```javascript
const { test, expect } = require('@playwright/test');

const items = ['RG-0001', 'RG-0008', 'RG-0002', 'RG-0003'];
const viewports = [
  { width: 1920, height: 1080, name: 'desktop' },
  { width: 768, height: 1024, name: 'tablet' },
  { width: 390, height: 844, name: 'mobile' }
];

for (const item of items) {
  for (const viewport of viewports) {
    test(`${item} - ${viewport.name} - front side`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto(`http://localhost:8000/${item}/`);
      
      // Wait for fonts and images to load
      await page.waitForLoadState('networkidle');
      
      // Take screenshot
      await expect(page).toHaveScreenshot(`${item}-${viewport.name}-front.png`);
      
      // Check that footer is visible
      const footer = page.locator('.front-footer');
      await expect(footer).toBeVisible();
      
      // Check that all footer content is visible
      const price = page.locator('.item-price');
      await expect(price).toBeVisible();
      
      const hint = page.locator('.flip-hint');
      await expect(hint).toBeVisible();
    });

    test(`${item} - ${viewport.name} - back side`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto(`http://localhost:8000/${item}/`);
      await page.waitForLoadState('networkidle');
      
      // Flip the card
      await page.click('.flip-card');
      await page.waitForTimeout(1000); // Wait for flip animation
      
      // Take screenshot
      await expect(page).toHaveScreenshot(`${item}-${viewport.name}-back.png`);
      
      // Check that back footer is visible
      const backFooter = page.locator('.back-footer');
      await expect(backFooter).toBeVisible();
      
      const buyButton = page.locator('.buy-button');
      await expect(buyButton).toBeVisible();
    });
  }
}
```

### DOM Structure Validation

Create `test-dom-structure.js`:

```javascript
const { JSDOM } = require('jsdom');
const fs = require('fs');

function validateItemCard(itemPath) {
  const html = fs.readFileSync(`${itemPath}/index.html`, 'utf8');
  const dom = new JSDOM(html);
  const doc = dom.window.document;
  
  const errors = [];
  
  // Check for required structure
  if (!doc.querySelector('.flip-card')) {
    errors.push('Missing .flip-card container');
  }
  
  if (!doc.querySelector('.card-face.card-front')) {
    errors.push('Missing .card-front');
  }
  
  if (!doc.querySelector('.card-face.card-back')) {
    errors.push('Missing .card-back');
  }
  
  if (!doc.querySelector('.item-image-container')) {
    errors.push('Missing .item-image-container');
  }
  
  if (!doc.querySelector('.front-info')) {
    errors.push('Missing .front-info');
  }
  
  if (!doc.querySelector('.front-footer')) {
    errors.push('Missing .front-footer');
  }
  
  if (!doc.querySelector('.back-footer')) {
    errors.push('Missing .back-footer');
  }
  
  // Check for CSS properties in style tag
  const style = doc.querySelector('style').textContent;
  
  if (!style.includes('min-height: 0')) {
    errors.push('CSS missing: min-height: 0 on image container');
  }
  
  if (!style.includes('flex-shrink: 0')) {
    errors.push('CSS missing: flex-shrink: 0 on footer');
  }
  
  if (!style.includes('aspect-ratio: 5 / 7')) {
    errors.push('CSS missing: aspect-ratio: 5 / 7');
  }
  
  return errors;
}

// Test all items
const items = ['RG-0001', 'RG-0002', 'RG-0003', 'RG-0008'];
let allPassed = true;

for (const item of items) {
  console.log(`Testing ${item}...`);
  const errors = validateItemCard(item);
  
  if (errors.length > 0) {
    console.log(`❌ FAILED: ${item}`);
    errors.forEach(err => console.log(`  - ${err}`));
    allPassed = false;
  } else {
    console.log(`✅ PASSED: ${item}`);
  }
}

process.exit(allPassed ? 0 : 1);
```

## Pre-Deploy Checklist Script

Create `pre-deploy.sh`:

```bash
#!/bin/bash
# Run all validation before deploying

set -e

echo "🧪 Running pre-deployment tests..."
echo ""

# 1. Validate all items exist
echo "📁 Checking item folders..."
for item in RG-000{1..9}; do
    if [ -d "$item" ]; then
        echo "  ✅ $item exists"
    fi
done
echo ""

# 2. Run CSS validation
echo "🎨 Validating CSS..."
for item in RG-000{1..9}; do
    if [ -d "$item" ]; then
        ./test-css-requirements.sh "$item" || exit 1
    fi
done
echo ""

# 3. Validate images
echo "🖼️  Checking images..."
for item in RG-000{1..9}; do
    if [ -d "$item" ]; then
        if [ ! -f "$item/hero.jpeg" ] && [ ! -f "$item/hero.png" ]; then
            echo "  ❌ $item: Missing hero image"
            exit 1
        fi
        if [ ! -f "$item/qr-code.png" ]; then
            echo "  ❌ $item: Missing qr-code.png"
            exit 1
        fi
        echo "  ✅ $item images present"
    fi
done
echo ""

# 4. Run DOM structure tests
echo "🏗️  Validating DOM structure..."
node test-dom-structure.js || exit 1
echo ""

# 5. Start local server and run visual tests
echo "🌐 Starting local server..."
python3 -m http.server 8000 &
SERVER_PID=$!
sleep 2

echo "📸 Running visual regression tests..."
npx playwright test || {
    kill $SERVER_PID
    exit 1
}

kill $SERVER_PID
echo ""

echo "✅ All tests passed! Safe to deploy."
```

## Usage

### Before Every Commit
```bash
# Make your changes
vim RG-0001/index.html

# Run validation
./validate-item.sh RG-0001

# Test locally
python3 -m http.server 8000
# Visit http://localhost:8000/RG-0001/

# Run full pre-deploy suite
./pre-deploy.sh

# If all pass, commit and push
git add RG-0001/index.html
git commit -m "Fix RG-0001 issue"
git push origin main
```

### Setting up CI (Optional)

Add `.github/workflows/test.yml`:

```yaml
name: Test Item Cards

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install -D @playwright/test jsdom
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Run validation tests
        run: |
          chmod +x pre-deploy.sh
          ./pre-deploy.sh
      
      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: test-results/
```

## Common Issues to Test For

1. **Content Cutoff**
   - Footer not visible on desktop
   - Image pushing content off screen
   
2. **Footer Alignment**
   - Front and back footers at different heights
   - 3D transform causing visual drift
   
3. **Image Issues**
   - Missing images (404 errors)
   - Images too large (> 1MB)
   - Images wrong aspect ratio
   
4. **Responsive Issues**
   - Card too tall on mobile
   - Text overflow on small screens
   - Touch targets too small (< 44px)
   
5. **Accessibility**
   - Missing alt text
   - No keyboard navigation
   - Poor color contrast
   - Missing ARIA labels
