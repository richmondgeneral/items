#!/usr/bin/env python3
"""Roll the canonical 'Tap for Story' chip into the inline-style item pages.

Skips RG-0014 (old 'pill over image' structure, edited by hand). Idempotent.
"""
import re, glob, sys

CHIP = """.flip-hint {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--rg-brown);
            background: var(--rg-cream);
            border: 1px solid rgba(107, 68, 35, 0.18);
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            line-height: 1;
        }

        @media (prefers-reduced-motion: no-preference) {
            .flip-icon { animation: flip-nudge 1.4s ease 0.9s 2; transform-origin: center; }
            @keyframes flip-nudge { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.18); } }
        }"""

changed, errors = [], []
for f in sorted(glob.glob("RG-*/index.html")):
    if f.startswith("RG-0014"):   # old structure, handled by hand
        continue
    html = open(f, encoding="utf-8").read()
    orig = html
    m = re.search(r"\.flip-hint\s*\{[^}]*\}", html)
    if not m:
        errors.append(f"{f}: no .flip-hint rule found"); continue
    if "position: absolute" in m.group(0):
        errors.append(f"{f}: unexpected pill-style .flip-hint (skipped)"); continue
    if "flip-nudge" not in html:            # idempotency: only insert once
        html = html[:m.start()] + CHIP + html[m.end():]
    html = html.replace("Tap for story", "Tap for Story").replace("Tap to learn more", "Tap for Story")
    if html != orig:
        open(f, "w", encoding="utf-8").write(html); changed.append(f)

print(f"changed {len(changed)} files")
if errors:
    print("ERRORS:\n" + "\n".join(errors)); sys.exit(1)
