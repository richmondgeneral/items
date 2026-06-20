#!/usr/bin/env python3
"""Verify the canonical 'Tap for Story' flip-hint chip across all item pages."""
import re, sys, glob

BAD_WORDING = ("Tap for story", "Tap for details", "Tap to learn more")
fails = []
for f in sorted(glob.glob("RG-*/index.html")):
    html = open(f, encoding="utf-8").read()
    # 1) exactly one .flip-hint rule, and it is the chip (has border-radius: 999px)
    m = re.search(r"\.flip-hint\s*\{[^}]*\}", html)
    if not m or "border-radius: 999px" not in m.group(0):
        fails.append(f"{f}: .flip-hint is not the chip rule")
    # 2) reduced-motion nudge present
    if "flip-nudge" not in html or "prefers-reduced-motion" not in html:
        fails.append(f"{f}: missing reduced-motion flip-nudge")
    # 3) canonical wording, no stale variants
    if "Tap for Story" not in html:
        fails.append(f"{f}: missing 'Tap for Story'")
    for bad in BAD_WORDING:
        if bad in html:
            fails.append(f"{f}: still contains '{bad}'")
    # 4) print still hides the hint (must NOT be removed)
    if not re.search(r"@media print[\s\S]*?\.flip-hint[\s\S]*?display\s*:\s*none", html):
        fails.append(f"{f}: print no longer hides .flip-hint")

print("\n".join(fails) if fails else "ALL ITEM PAGES OK")
sys.exit(1 if fails else 0)
