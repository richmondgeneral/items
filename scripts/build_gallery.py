#!/usr/bin/env python3
"""Idempotent gallery reconciler for items/index.html.

The Shop gallery (`items/index.html`, the `.items-grid`) is the GitHub-Pages
landing grid. Historically a new item's card was injected by a hand-run `sed`
step (rg-full-auto Phase 7 / info-card-publishing.md). That step was brittle and
easy to skip, so Listed items repeatedly went live as standalone pages while
never appearing in the grid (RG-0028/0029/0034/0052/0053/0054).

This script replaces that step with a deterministic, idempotent reconcile:

  build_gallery.py            # apply: insert a card for every Listed/Sold item
  build_gallery.py --apply    #   that is missing one (default mode)
  build_gallery.py --check    # gate: exit 1 if any Listed/Sold item lacks a card
  build_gallery.py --dry-run  # show what would change, write nothing

Design guarantees
-----------------
* INSERT-ONLY. Existing cards are never edited or removed, so curated editorial
  copy (titles, era lines, category labels) is preserved. Re-running is a no-op.
* SKU ORDER. New cards are inserted at their correct ascending-SKU position.
* Cards are derived from items/RG-XXXX/label.json. An item belongs in the
  gallery when its `state` is Listed or Sold.

`--check` is the verification gate: wire it into the listing workflow / reconcile
so a Listed item can never silently miss the grid again.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # items/
INDEX = os.path.join(ROOT, "index.html")
PLACEHOLDER = "<!-- Coming Soon Placeholder -->"

# An item with one of these states should have a gallery card.
GALLERY_STATES = {"Listed", "Sold"}

# The "New" badge is client-side and AUTO-EXPIRING: each active card carries
# data-added (from label.json added_at), and this script injects the badge only
# when within NEW_DAYS of now — so it disappears on its own with no rebuild, and
# editing/re-committing an old item never re-flags it as new. NEW_DAYS lives here
# (one source of truth). Sold badges stay server-rendered.
NEW_BADGE_JS = """    <!-- NEW_BADGE: client-side, auto-expiring New badge from data-added -->
    <script>
      (() => {
        const NEW_DAYS = 30;
        const now = Date.now();
        document.querySelectorAll('.item-card[data-added]:not([data-status="sold"])').forEach(card => {
          const t = Date.parse(card.dataset.added);
          if (isNaN(t) || (now - t) / 86400000 > NEW_DAYS) return;
          const img = card.querySelector('.item-image');
          if (img && !img.querySelector('.item-badge')) {
            const s = document.createElement('span');
            s.className = 'item-badge';
            s.textContent = 'New';
            img.prepend(s);
          }
        });
      })();
    </script>
"""

# reporting-category text -> data-category filter slug (first keyword wins).
# Slugs must match the filter tabs in index.html:
#   all / tech / books / media / wearables / pottery / furniture / collectibles
_SLUG_RULES = [
    ("book", "books"),
    ("ceramic", "pottery"), ("pottery", "pottery"), ("glass", "pottery"),
    ("furniture", "furniture"),
    ("compute", "tech"), ("electronic", "tech"), ("tech", "tech"),
    ("analog", "media"), ("media", "media"), ("film", "media"),
    ("wearable", "wearables"), ("apparel", "wearables"),
    ("cloth", "wearables"), ("jewel", "wearables"),
    ("collectible", "collectibles"),
]


def slug_for(repcat: str) -> str:
    s = repcat.lower()
    for needle, slug in _SLUG_RULES:
        if needle in s:
            return slug
    return "collectibles"  # catch-all (matches the SOP category table)


def clean_cat(repcat: str) -> str:
    """'Pottery & Ceramics (reporting)' -> 'Pottery & Ceramics'."""
    return re.sub(r"\s*\(reporting\)\s*$", "", repcat).strip()


def attr_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace('"', "&quot;")


def reporting_category(label: dict) -> str:
    note = label.get("reporting_category_note")
    if note:
        return note
    cats = label.get("channels", {}).get("square", {}).get("categories", [])
    for c in cats:
        c = clean_cat(c)
        if c and c.lower() not in ("new arrivals", "new finds"):
            return c
    return "Collectibles"


def is_sold(label: dict) -> bool:
    if str(label.get("state", "")).strip().lower() == "sold":
        return True
    chans = label.get("channels", {})
    return any(str(c.get("status", "")).lower() == "sold" for c in chans.values()
               if isinstance(c, dict))


def card_fields(sku: str, label: dict) -> dict:
    product = label.get("product_name", sku)
    # Card title: trim the descriptive tail after an em-dash; the rest goes to the era line.
    title = re.split(r"\s+—\s+", product, maxsplit=1)[0].strip() or product
    repcat = clean_cat(reporting_category(label))
    # Era line: first up-to-3 segments of the attributes string.
    attrs = label.get("attributes", "") or ""
    segs = [s.strip() for s in re.split(r"[•·]", attrs) if s.strip()]
    era = " • ".join(segs[:3]) if segs else repcat
    hero = label.get("photos", {}).get("hero") or "hero.png"
    # Prefer the uniform transparent card.png (matte.py output) when present;
    # fall back to the raw hero so un-matted items still render.
    image = "card.png" if os.path.isfile(os.path.join(ROOT, sku, "card.png")) else hero
    price = str(label.get("price", "")).strip()
    if price and not price.startswith("$"):
        price = "$" + price
    return {
        "sku": sku,
        "slug": slug_for(repcat),
        "category": repcat,
        "title": title,
        "era": era,
        "hero": hero,
        "image": image,
        "transparent": image == "card.png",
        "added": label.get("added_at", ""),
        "price": price or "$0",
        "alt": attr_escape(product),
        "sold": is_sold(label),
    }


def render_card(f: dict) -> str:
    """Render a single 12-space-indented card block (comment + anchor), no trailing newline."""
    if f["sold"]:
        status_attr = ' data-status="sold"'
        badge_line = '                    <span class="item-badge sold">Sold</span>\n'
        price = f'<span class="item-price sold">Sold · {f["price"]}</span>'
        cta = "View Archive"
    else:
        status_attr = ""
        badge_line = ""  # "New" is injected client-side from data-added (auto-expiring)
        price = f'<span class="item-price">{f["price"]}</span>'
        cta = "View Story"
    img_attr = ' data-img="card"' if f.get("transparent") else ""
    added_attr = f' data-added="{f["added"]}"' if f.get("added") else ""
    return (
        f'            <!-- {f["sku"]}: {f["title"]} -->\n'
        f'            <a href="./{f["sku"]}/" class="item-card" data-category="{f["slug"]}"{status_attr}{img_attr}{added_attr}>\n'
        f'                <div class="item-image">\n'
        f'{badge_line}'
        f'                    <span class="item-sku">{f["sku"]}</span>\n'
        f'                    <img src="./{f["sku"]}/{f["image"]}" alt="{f["alt"]}" style="max-width: 100%; max-height: 200px; object-fit: contain; border-radius: 4px;">\n'
        f'                </div>\n'
        f'                <div class="item-info">\n'
        f'                    <p class="item-category">{f["category"]}</p>\n'
        f'                    <h3 class="item-title">{f["title"]}</h3>\n'
        f'                    <p class="item-era">{f["era"]}</p>\n'
        f'                    <div class="item-footer">\n'
        f'                        {price}\n'
        f'                        <span class="view-story">\n'
        f'                            {cta}\n'
        f'                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n'
        f'                                <path d="M5 12h14M12 5l7 7-7 7"/>\n'
        f'                            </svg>\n'
        f'                        </span>\n'
        f'                    </div>\n'
        f'                </div>\n'
        f'            </a>'
    )


def load_items() -> dict:
    """sku -> label dict, for every items/RG-XXXX/label.json."""
    out = {}
    for lj in glob.glob(os.path.join(ROOT, "RG-*", "label.json")):
        sku = os.path.basename(os.path.dirname(lj))
        try:
            out[sku] = json.load(open(lj, encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ! skipping {sku}: {e}", file=sys.stderr)
    return out


def carded_skus(text: str) -> dict:
    """sku -> char index of the start of its comment line, for cards in the grid."""
    out = {}
    pat = re.compile(
        r'(?m)^[ \t]*<!-- (RG-\d{4})\b[^\n]*-->\n[ \t]*<a href="\./\1/" class="item-card"'
    )
    for m in pat.finditer(text):
        out[m.group(1)] = m.start()
    return out


def should_be_carded(items: dict) -> set:
    return {sku for sku, lab in items.items()
            if str(lab.get("state", "")).strip() in GALLERY_STATES}


def recount(text: str) -> str:
    """Set the static #item-count to the number of non-sold cards (mirrors the page JS)."""
    cards = re.findall(r'<a [^>]*class="item-card"[^>]*>', text)
    available = sum(1 for c in cards if 'data-status="sold"' not in c)
    return re.sub(
        r'(<div class="stat-number" id="item-count">)\d*(</div>)',
        rf'\g<1>{available}\g<2>', text, count=1,
    )


def reconcile(text: str, items: dict):
    existing = carded_skus(text)
    want = should_be_carded(items)
    missing = sorted(want - set(existing))

    pm = re.search(r'(?m)^[ \t]*' + re.escape(PLACEHOLDER), text)
    if not pm:
        raise SystemExit("ERROR: placeholder anchor not found in index.html")
    placeholder_pos = pm.start()

    # Compute insertion (pos, sku, block) against the ORIGINAL text.
    inserts = []
    skipped = []
    for sku in missing:
        item_dir = os.path.join(ROOT, sku)
        hero = items[sku].get("photos", {}).get("hero") or "hero.png"
        if not os.path.isfile(os.path.join(item_dir, hero)):
            skipped.append((sku, f"hero image '{hero}' missing"))
            continue
        higher = sorted(s for s in existing if s > sku)
        pos = existing[higher[0]] if higher else placeholder_pos
        block = render_card(card_fields(sku, items[sku]))
        inserts.append((pos, sku, block))

    # Apply from highest pos to lowest; for equal pos, higher sku first so final order ascends.
    for pos, sku, block in sorted(inserts, key=lambda t: (t[0], t[1]), reverse=True):
        text = text[:pos] + block + "\n\n            " + text[pos:].lstrip(" \t")

    inserted = [sku for _, sku, _ in inserts]
    text = recount(text)
    return text, inserted, skipped, missing


def relink_cards(text: str, only=None):
    """Opt-in: switch EXISTING cards to card.png where the file now exists.

    Not part of the insert-only default — run explicitly after matte.py has
    generated card.png for items. Adds data-img="card" so CSS can color behind.
    `only` (a set of SKUs) limits the relink to those items.
    """
    changed = []
    for sku in sorted(carded_skus(text)):
        if only and sku not in only:
            continue
        if not os.path.isfile(os.path.join(ROOT, sku, "card.png")):
            continue
        if re.search(rf'src="\./{sku}/card\.png"', text):
            continue  # already linked
        text = re.sub(rf'(src="\./{sku}/)[^"]+\.(?:png|jpe?g|jpg)"',
                      r'\1card.png"', text, count=1)

        def _add_attr(m):
            tag = m.group(0)
            return tag if "data-img=" in tag else tag[:-1] + ' data-img="card">'
        text = re.sub(rf'<a href="\./{sku}/" class="item-card"[^>]*>', _add_attr, text, count=1)
        changed.append(sku)
    return text, changed


def rebadge(text: str, items: dict):
    """Switch existing cards to the date-driven, auto-expiring New badge (opt-in).

    Strips baked plain 'New' spans (Sold badges are kept), stamps data-added from
    each item's label.json onto its carded anchor, and ensures NEW_BADGE_JS is present.
    """
    text, removed = re.subn(r'[ \t]*<span class="item-badge">New</span>\n', '', text)
    stamped = []
    for sku in sorted(carded_skus(text)):
        added = (items.get(sku) or {}).get("added_at")
        if not added or re.search(rf'<a href="\./{sku}/"[^>]*data-added=', text):
            continue

        def _add(m):
            tag = m.group(0)
            return tag if "data-added=" in tag else tag[:-1] + f' data-added="{added}">'
        new = re.sub(rf'<a href="\./{sku}/" class="item-card"[^>]*>', _add, text, count=1)
        if new != text:
            text = new
            stamped.append(sku)
    if "NEW_BADGE:" not in text:
        text = text.replace("</body>", NEW_BADGE_JS + "</body>", 1)
    return text, removed, stamped


def main() -> int:
    ap = argparse.ArgumentParser(description="Idempotent gallery reconciler for items/index.html")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true", help="insert missing cards and write (default)")
    g.add_argument("--check", action="store_true", help="exit 1 if any Listed/Sold item lacks a card")
    g.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
    g.add_argument("--relink-cards", action="store_true",
                   help="switch existing cards to card.png where present (opt-in)")
    g.add_argument("--rebadge", action="store_true",
                   help="switch existing cards to the date-driven auto-expiring New badge (opt-in)")
    ap.add_argument("--sku", nargs="*", default=None,
                    help="limit --relink-cards to these SKUs (e.g. --sku RG-0002)")
    args = ap.parse_args()

    text = open(INDEX, encoding="utf-8").read()
    items = load_items()

    if args.relink_cards:
        new_text, changed = relink_cards(text, only=set(args.sku) if args.sku else None)
        if not changed:
            print("No cards to relink (no card.png present for existing cards).")
            return 0
        with open(INDEX, "w", encoding="utf-8") as fh:
            fh.write(new_text)
        print(f"Relinked {len(changed)} card(s) to card.png: {', '.join(changed)}")
        return 0

    if args.rebadge:
        new_text, removed, stamped = rebadge(text, items)
        with open(INDEX, "w", encoding="utf-8") as fh:
            fh.write(new_text)
        print(f"Rebadge: removed {removed} baked 'New' badge(s), stamped data-added on "
              f"{len(stamped)} card(s); auto-expiring JS ensured.")
        return 0

    if args.check:
        existing = set(carded_skus(text))
        want = should_be_carded(items)
        missing = sorted(want - existing)
        # Also flag cards that point at an item dir which no longer exists.
        orphans = sorted(sku for sku in existing
                         if not os.path.isdir(os.path.join(ROOT, sku)))
        if not missing and not orphans:
            print(f"OK: gallery in sync — {len(want)} Listed/Sold items, all carded.")
            return 0
        if missing:
            print(f"FAIL: {len(missing)} Listed/Sold item(s) missing a gallery card:")
            for sku in missing:
                print(f"  - {sku}  ({items[sku].get('product_name','?')})")
        if orphans:
            print(f"FAIL: {len(orphans)} gallery card(s) point at a missing item dir: {', '.join(orphans)}")
        print("\nRun: python items/scripts/build_gallery.py --apply")
        return 1

    new_text, inserted, skipped, missing = reconcile(text, items)
    for sku, why in skipped:
        print(f"  ! skipped {sku}: {why} (intake incomplete)")
    if not inserted:
        print(f"Gallery already in sync ({len(should_be_carded(items))} Listed/Sold items, no cards to add).")
        return 0
    print(f"Cards to insert ({len(inserted)}): {', '.join(inserted)}")
    if args.dry_run:
        print("(--dry-run: nothing written)")
        return 0
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    print(f"Wrote {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
