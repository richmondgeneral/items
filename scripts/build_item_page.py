#!/usr/bin/env python3
"""Deterministic item-page generator: render items/RG-XXXX/index.html from label.json.

label.json is the SINGLE SOURCE OF TRUTH. Structured fields (price, links, image,
dimensions, era, QR, fulfillment) are ALWAYS derived from it — this is what kills
the stale-price / stale-link drift the hand-built pages kept producing. Curated
editorial prose lives in an OPTIONAL `page` block in label.json; when a `page`
field is absent, a mechanical fallback is derived from the structured data.

The page format reproduced here is the RG-0055 flip-card (the canonical template):
inline <style>, a flip handler, and a view-time price formatter that strips a
trailing ``.00`` visually (so the SOURCE keeps ``$65.00`` — never pre-strip it).

HTML-escaping rule
------------------
* Curated ``page.*`` strings may contain intentional HTML entities (``&mdash;``,
  ``&Prime;``, …) → inserted AS-IS (trusted authoring input).
* Mechanically-derived fallback text (from product_name / attributes /
  condition_notes) → run through ``html.escape`` (plain UTF-8 source; literal
  em-dashes stay literal ``—``, which is fine).

Usage
-----
  build_item_page.py RG-0055            # write items/RG-0055/index.html
  build_item_page.py --all              # (re)generate every items/RG-*/
  build_item_page.py RG-0055 --dry-run  # print first ~40 lines, write nothing
  build_item_page.py --all --check      # exit 1 if any page drifts from label.json
  build_item_page.py --all --check --managed-only  # drift-check only generator-managed
                                        # items (label has a `page` block); the CI gate
                                        # uses this so legacy hand-curated pages don't fail
  build_item_page.py RG-0055 --force    # write even if protected / sold

Living-test pages (TILT/iridescent RG-0001, variant-stack RG-0011/0027, the
RG-0027 /buy/ redirect) and Sold pages are PROTECTED: they are skipped unless
``--force`` is given, so their bespoke markup/JS is never clobbered.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # items/
PAGES_BASE = "https://richmondgeneral.github.io/items"

# Approx max length for the SEO meta description (truncate at a word boundary).
SEO_DESC_MAX = 155

# Markers that mean "this page is a living experiment or a sold archive" — never
# overwrite it without --force. These are STRUCTURAL (class / data-attribute /
# HTML-comment sentinel) forms that cannot plausibly appear in curated prose:
# a Listed item whose story merely says the word "sold" or "variant-stack" must
# NOT be mistaken for protected (that would silently defeat regen / the reprice
# cascade). Verified against the real pages on disk:
#   RG-0001       TILT / iridescent foil
#   RG-0011       As-Found/As-Restored variant-stack slider
#   RG-0027       /buy/ redirect layer + variant-stack + sold archive
#   RG-0002/0027  sold-archive pattern
_PROTECTED_MARKERS = (
    # variant-stack slider (RG-0011, RG-0027)
    'class="variant-stack"',
    'data-mode="slider"',
    "data-variant=",
    # TILT / iridescent foil (RG-0001)
    'data-finish="iridescent"',
    'class="iri-foil"',
    "IRIDESCENT FOIL CONTROLLER",
    # /buy/ redirect layer (RG-0027/buy/index.html)
    "BUY REDIRECT LAYER",
    # sold archive (RG-0002, RG-0027): the exact class combo + the panel/status
    'class="sku-badge sold-badge"',
    'class="sold-status-panel"',
    'data-status="sold"',
)


# ---------------------------------------------------------------------------
# Pure derivations (no I/O).
# ---------------------------------------------------------------------------

def _product(label: dict) -> str:
    return str(label.get("product_name") or label.get("sku") or "")


def _page(label: dict) -> dict:
    p = label.get("page")
    return p if isinstance(p, dict) else {}


def _plain_card_title(label: dict) -> str:
    """Mechanical card title — product_name pre-em-dash, plain UTF-8 (no entities).

    Used for attribute contexts (aria-label, img alt) where we always want the
    derived plain text and html.escape it, so a curated entity-bearing
    ``page.card_title`` is never double-encoded into an attribute.
    """
    product = _product(label)
    return re.split(r"\s+—\s+", product, maxsplit=1)[0].strip() or product


def card_title(label: dict) -> str:
    """Curated ``page.card_title`` else product_name split at the first em-dash."""
    cur = _page(label).get("card_title")
    if cur:
        return cur
    return _plain_card_title(label)


def seo_title(label: dict) -> str:
    """Curated ``page.seo_title`` else the card title."""
    return _page(label).get("seo_title") or card_title(label)


def era_line(label: dict) -> str:
    """Curated ``page.era_line`` else first <=3 attribute segments + circa value.

    Fallback = first <=3 ``attributes`` segments, then ``estimates.circa.value``
    appended (when present and not already the last segment), joined by ' • '
    (per the P0 design). So a label with no curated era still surfaces its era.
    """
    cur = _page(label).get("era_line")
    if cur:
        return cur
    attrs = str(label.get("attributes") or "")
    segs = [s.strip() for s in re.split(r"[•·]", attrs) if s.strip()][:3]
    circa = str((((label.get("estimates") or {}).get("circa")) or {}).get("value") or "").strip()
    if circa and (not segs or segs[-1] != circa):
        segs.append(circa)
    return " • ".join(segs)


def story(label: dict) -> str:
    """Curated ``page.story`` else condition_notes verbatim."""
    cur = _page(label).get("story")
    if cur:
        return cur
    return str(label.get("condition_notes") or "")


def seo_description(label: dict) -> str:
    """Curated ``page.seo_description`` else condition_notes truncated at a word boundary."""
    cur = _page(label).get("seo_description")
    if cur:
        return cur
    text = str(label.get("condition_notes") or "").strip()
    if len(text) <= SEO_DESC_MAX:
        return text
    cut = text[:SEO_DESC_MAX]
    sp = cut.rfind(" ")
    if sp > 0:
        cut = cut[:sp]
    return cut.rstrip(" ,;.")


def dims_str(dimensions_in: dict) -> str:
    """Render the dimensions block from whatever keys are present.

    diameter present       -> ``{height}&Prime; H &times; {diameter}&Prime; dia``
    height/width/depth      -> ``{h} &times; {w} &times; {d} in``
    otherwise               -> join available ``k v`` pairs (or "" if empty).
    Uses the ``&Prime;`` entity for inches, consistent with RG-0055.
    """
    if not isinstance(dimensions_in, dict):
        return ""
    d = {k: v for k, v in dimensions_in.items()
         if not (isinstance(v, (str, type(None))) and not v) and not isinstance(v, (dict, list))}

    def num(v):
        # Render 18.0 as "18" but 12.5 as "12.5".
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)

    if d.get("diameter") not in (None, ""):
        h = d.get("height")
        if h not in (None, ""):
            return f"{num(h)}&Prime; H &times; {num(d['diameter'])}&Prime; dia"
        return f"{num(d['diameter'])}&Prime; dia"
    if any(d.get(k) not in (None, "") for k in ("height", "width", "depth")):
        parts = [num(d[k]) for k in ("height", "width", "depth") if d.get(k) not in (None, "")]
        return " &times; ".join(parts) + " in"
    # Fallback: join remaining scalar pairs (excluding bookkeeping keys).
    skip = {"est", "confidence", "basis", "measured_at", "note", "refine_with", "_note"}
    pairs = [f"{k} {num(v)}" for k, v in d.items() if k not in skip]
    return ", ".join(pairs)


def details(label: dict) -> dict:
    """The four detail cells (Maker / Era / Dimensions / Condition).

    Curated ``page.details`` wins outright (used as-is). Otherwise derive each:
      Maker      = identity.maker (+ ", {maker_location}" if present)
      Era        = estimates.circa.value (+ " (est.)" if circa.est truthy)
      Dimensions = dims_str(estimates.dimensions_in)
      Condition  = first clause of `condition` (split on em-dash / ';')
    Returns a dict with keys Maker/Era/Dimensions/Condition (values may be "").
    A curated ``details`` dict is returned verbatim.
    """
    cur = _page(label).get("details")
    if isinstance(cur, dict):
        return cur

    identity = label.get("identity") or {}
    maker = str(identity.get("maker") or "")
    loc = str(identity.get("maker_location") or "")
    if maker and loc:
        maker = f"{maker} ({loc})"

    est = label.get("estimates") or {}
    circa = est.get("circa") or {}
    era = str(circa.get("value") or "")
    if era and circa.get("est"):
        era = f"{era} (est.)"

    dims = dims_str(est.get("dimensions_in") or {})

    cond = str(label.get("condition") or "")
    cond_first = re.split(r"\s*[—;]\s*", cond, maxsplit=1)[0].strip()

    return {"Maker": maker, "Era": era, "Dimensions": dims, "Condition": cond_first}


def main_image(label: dict) -> str:
    """Relative path to the front hero image: cutout, else hero, else hero.jpeg."""
    photos = label.get("photos") or {}
    name = photos.get("cutout") or photos.get("hero") or "hero.jpeg"
    return "./" + name


def _cutout_name(label: dict) -> str:
    photos = label.get("photos") or {}
    return photos.get("cutout") or photos.get("hero") or "hero.jpeg"


def qr_buy_file(label: dict, item_dir) -> str:
    """``qr_codes.buy.file`` if set, else qr-buy.png if it exists, else qr-code.png."""
    qr = (label.get("qr_codes") or {}).get("buy") or {}
    if qr.get("file"):
        return qr["file"]
    if item_dir is not None and os.path.isfile(os.path.join(str(item_dir), "qr-buy.png")):
        return "qr-buy.png"
    return "qr-code.png"


def buy_link(label: dict) -> str:
    """``channels.square.buy_link`` (may be empty for un-listed items) else '#'."""
    link = ((label.get("channels") or {}).get("square") or {}).get("buy_link")
    return link or "#"


def fulfillment_line(label: dict) -> str:
    """'Local pickup only' for pickup-only items, else 'Ships or local pickup'."""
    if str(label.get("fulfillment") or "") == "local_pickup_only":
        return "Local pickup only"
    if (label.get("shipping") or {}).get("local_pickup_only"):
        return "Local pickup only"
    return "Ships or local pickup"


# ---------------------------------------------------------------------------
# Template (RG-0055, the canonical format). Dynamic spans are __TOKEN__ markers
# replaced by str.replace — NOT str.format — because the CSS/JS bodies are full
# of literal { } braces. The two trailing <script> blocks are preserved verbatim.
# ---------------------------------------------------------------------------

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__SEO_TITLE__ | Richmond General</title>
<meta name="description" content="__SEO_DESC__">
<meta property="og:title" content="__SEO_TITLE__ | Richmond General"><meta property="og:description" content="__SEO_DESC__">
<meta property="og:image" content="__OG_IMAGE__"><meta property="og:url" content="https://richmondgeneral.github.io/items/__SKU__/"><meta property="og:type" content="product">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+Pro:wght@300;400;600&display=swap" rel="stylesheet">
<style>
:root { --rg-gold:#C9A961; --rg-cream:#F5F1E8; --rg-charcoal:#2C2C2C; --rg-brown:#6B4423; --rg-shadow:rgba(44,44,44,0.15); }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Source Sans Pro',sans-serif; background:linear-gradient(135deg,#F5F1E8 0%,#E8E2D5 100%); min-height:100vh; display:flex; justify-content:center; align-items:center; padding:2rem; }
.card-container { perspective:1500px; width:100%; max-width:420px; }
.flip-card { position:relative; width:100%; aspect-ratio:5/7; min-height:550px; cursor:pointer; transform-style:preserve-3d; transition:transform 0.8s cubic-bezier(0.4,0,0.2,1); }
.flip-card.flipped { transform:rotateY(180deg); }
.card-face { position:absolute; width:100%; height:100%; backface-visibility:hidden; border-radius:12px; box-shadow:0 20px 60px var(--rg-shadow); overflow:hidden; background:white; }
.card-front { display:flex; flex-direction:column; }
.item-image-container { flex:1 1 0; min-height:0; background:var(--rg-cream); display:flex; align-items:center; justify-content:center; padding:1.5rem; position:relative; }
.item-image { max-width:100%; max-height:100%; object-fit:contain; border-radius:4px; }
.sku-badge { position:absolute; z-index:2; top:1rem; right:1rem; background:var(--rg-charcoal); color:white; font-size:0.7rem; font-weight:600; padding:0.3rem 0.6rem; border-radius:4px; letter-spacing:0.5px; }
.front-info { flex:0 0 auto; padding:1.25rem 1.5rem; background:white; border-top:3px solid var(--rg-gold); display:flex; flex-direction:column; }
.item-title { font-family:'Playfair Display',serif; font-size:1.25rem; font-weight:600; color:var(--rg-charcoal); line-height:1.3; margin-bottom:0.5rem; }
.item-era { font-size:0.85rem; color:var(--rg-brown); flex:1; margin-bottom:0.75rem; }
.front-footer { flex-shrink:0; height:44px; display:flex; justify-content:space-between; align-items:center; }
.item-price { font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:700; color:var(--rg-charcoal); }
.flip-hint { font-size:0.75rem; color:#888; display:flex; align-items:center; gap:0.3rem; }
.flip-icon { width:16px; height:16px; }
.card-back { transform:rotateY(180deg); display:flex; flex-direction:column; background:white; }
.back-header { background:var(--rg-charcoal); color:white; padding:1rem 1.5rem; display:flex; justify-content:space-between; align-items:center; }
.back-title { font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:600; }
.back-sku { font-size:0.75rem; opacity:0.8; }
.story-section { flex:1; padding:1.25rem 1.5rem; overflow-y:auto; }
.section-label { font-size:0.65rem; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; color:var(--rg-gold); margin-bottom:0.5rem; }
.story-text { font-size:0.9rem; line-height:1.6; color:var(--rg-charcoal); margin-bottom:1.25rem; }
.details-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:1.25rem; }
.detail-item { background:var(--rg-cream); padding:0.6rem 0.8rem; border-radius:6px; }
.detail-label { font-size:0.65rem; text-transform:uppercase; letter-spacing:0.5px; color:#666; margin-bottom:0.15rem; }
.detail-value { font-size:0.85rem; font-weight:600; color:var(--rg-charcoal); }
.back-footer { flex-shrink:0; min-height:80px; padding:1rem 1.5rem; background:var(--rg-cream); border-top:1px solid #ddd; display:flex; justify-content:space-between; align-items:center; }
.qr-section { display:flex; align-items:center; gap:0.75rem; }
.qr-code { width:60px; height:60px; background:white; padding:4px; border-radius:4px; }
.qr-code img { width:100%; height:100%; }
.qr-text { font-size:0.7rem; color:#666; line-height:1.4; }
.qr-text strong { display:block; color:var(--rg-charcoal); font-size:0.8rem; }
.buy-button { background:var(--rg-gold); color:white; border:none; padding:0.75rem 1.25rem; border-radius:6px; font-family:'Source Sans Pro',sans-serif; font-size:0.85rem; font-weight:600; cursor:pointer; text-decoration:none; }
.brand-strip { flex-shrink:0; text-align:center; padding:0.6rem; background:var(--rg-charcoal); color:white; font-size:0.7rem; letter-spacing:1px; }
.brand-strip a { color:var(--rg-gold); text-decoration:none; }
.flip-card:focus { outline:3px solid var(--rg-gold); outline-offset:4px; }
.sr-only { position:absolute; width:1px; height:1px; overflow:hidden; }
@media print { body { background:white; padding:0; } .flip-card { transform:none !important; } .card-face { position:relative; box-shadow:none; } .card-back { transform:rotateY(0) !important; page-break-before:always; } .flip-hint,.buy-button { display:none; } }
@media (max-width:600px) { body { padding:1rem; align-items:flex-start; } .flip-card { min-height:max(650px,85vh); aspect-ratio:auto; height:auto; } .card-face { position:absolute; height:auto; min-height:100%; } .card-front { display:flex; flex-direction:column; min-height:max(650px,85vh); } .card-back { position:absolute; min-height:max(650px,85vh); overflow-y:auto; } .details-grid { grid-template-columns:1fr; } .back-footer { flex-direction:column; gap:0.75rem; align-items:stretch; } .buy-button { width:100%; text-align:center; } }
</style></head>
<body>
<div class="card-container"><div class="flip-card" tabindex="0" role="button" aria-expanded="false" aria-label="__ARIA_LABEL__">
<div class="card-face card-front">
<div class="item-image-container"><span class="sku-badge">__SKU__</span><img src="__MAIN_IMAGE__" alt="__IMG_ALT__" class="item-image"></div>
<div class="front-info"><h1 class="item-title">__CARD_TITLE__</h1><p class="item-era">__ERA_LINE__</p>
<div class="front-footer"><span class="item-price">__PRICE__</span>
<span class="flip-hint"><svg class="flip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>Tap for story</span></div></div></div>
<div class="card-face card-back">
<div class="back-header"><span class="back-title">The Story</span><span class="back-sku">__SKU__</span></div>
<div class="story-section"><p class="section-label">The Story</p><p class="story-text">__STORY__</p>
<div class="details-grid">
<div class="detail-item"><p class="detail-label">Maker</p><p class="detail-value">__DETAIL_MAKER__</p></div>
<div class="detail-item"><p class="detail-label">Era</p><p class="detail-value">__DETAIL_ERA__</p></div>
<div class="detail-item"><p class="detail-label">Dimensions</p><p class="detail-value">__DETAIL_DIMENSIONS__</p></div>
<div class="detail-item"><p class="detail-label">Condition</p><p class="detail-value">__DETAIL_CONDITION__</p></div>
</div></div>
<div class="back-footer"><div class="qr-section"><div class="qr-code"><img src="./__QR_BUY__" alt="Scan to buy"></div><div class="qr-text"><strong>Scan to Buy</strong>__FULFILLMENT__</div></div>
<a href="__BUY_LINK__" class="buy-button">Buy Now</a></div>
<div class="brand-strip">RICHMOND GENERAL &middot; <a href="https://www.richmondgeneral.com">richmondgeneral.com</a></div></div>
</div></div>
<script>
const fc=document.querySelector('.flip-card');const ua=()=>fc.setAttribute('aria-expanded',fc.classList.contains('flipped'));
fc.addEventListener('click',()=>{fc.classList.toggle('flipped');ua();});
fc.addEventListener('keydown',(e)=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fc.classList.toggle('flipped');ua();}});
document.querySelector('.buy-button')?.addEventListener('click',(e)=>e.stopPropagation());
</script>
<script>(()=>{const p=/\\$([0-9]+)\\.00\\b/g;document.querySelectorAll('.item-price').forEach((el)=>{if(el.textContent)el.textContent=el.textContent.replace(p,'$$$1');});})();</script>
</body></html>
"""


def _price_str(label: dict) -> str:
    """Price as it must appear in the SOURCE: ``$65.00`` (two decimals, never pre-stripped)."""
    raw = str(label.get("price") or "").strip()
    raw = raw.lstrip("$").strip()
    if not raw:
        return "$0.00"
    try:
        return f"${float(raw):.2f}"
    except ValueError:
        return "$" + raw


def _attr_title(label: dict) -> str:
    """Plain-text card title for attribute contexts (aria-label, img alt).

    Uses the VISIBLE card title (curated ``page.card_title`` when present, else
    the mechanical one) but with HTML entities decoded to plain text, so the
    caller can html.escape() it for an attribute without double-encoding
    (``&mdash;`` -> ``—`` -> ``—``, never ``&amp;mdash;``).
    """
    return html.unescape(card_title(label))


def _img_alt(label: dict) -> str:
    """Deterministic alt text for the hero (visible title as plain text → escaped)."""
    return _attr_title(label)


def render_page(sku: str, label: dict, item_dir=None) -> str:
    """Fill the RG-0055 template from ``label``.

    Curated ``page.*`` text is inserted as-is (trusted entities); mechanically
    derived text is html-escaped. The two trailing <script> blocks are verbatim.
    og:image is the absolute GitHub Pages URL of the cutout (or hero fallback).
    """
    page = _page(label)

    def field(key, derive):
        """Curated value (as-is) when present in page block, else escaped derived value."""
        if page.get(key):
            return str(page[key])
        return html.escape(str(derive()))

    seo_t = field("seo_title", lambda: seo_title(label))
    seo_d = field("seo_description", lambda: seo_description(label))
    title = field("card_title", lambda: card_title(label))
    era = field("era_line", lambda: era_line(label))
    story_html = field("story", lambda: story(label))

    # Details: curated dict (as-is) vs derived (escaped). dims_str already emits
    # the &Prime;/&times; entities, so derived dims must NOT be re-escaped.
    det = details(label)
    if isinstance(page.get("details"), dict):
        dmaker = str(det.get("Maker", ""))
        dera = str(det.get("Era", ""))
        ddim = str(det.get("Dimensions", ""))
        dcond = str(det.get("Condition", ""))
    else:
        dmaker = html.escape(str(det.get("Maker", "")))
        dera = html.escape(str(det.get("Era", "")))
        ddim = str(det.get("Dimensions", ""))  # entity-bearing, trusted output of dims_str
        dcond = html.escape(str(det.get("Condition", "")))

    # aria-label / img alt derive from the VISIBLE card title as plain text
    # (entities decoded) then escaped, so a curated entity-bearing card_title
    # is never double-encoded into an attribute.
    aria = html.escape(_attr_title(label) + " info card")
    img_alt = html.escape(_img_alt(label))

    cutout = _cutout_name(label)
    og_image = f"{PAGES_BASE}/{sku}/{cutout}"

    repl = {
        "__SEO_TITLE__": seo_t,
        "__SEO_DESC__": seo_d,
        "__OG_IMAGE__": og_image,
        "__SKU__": html.escape(sku),
        "__ARIA_LABEL__": aria,
        "__MAIN_IMAGE__": main_image(label),
        "__IMG_ALT__": img_alt,
        "__CARD_TITLE__": title,
        "__ERA_LINE__": era,
        "__PRICE__": _price_str(label),
        "__STORY__": story_html,
        "__DETAIL_MAKER__": dmaker,
        "__DETAIL_ERA__": dera,
        "__DETAIL_DIMENSIONS__": ddim,
        "__DETAIL_CONDITION__": dcond,
        "__QR_BUY__": qr_buy_file(label, item_dir),
        "__FULFILLMENT__": html.escape(fulfillment_line(label)),
        "__BUY_LINK__": html.escape(buy_link(label), quote=True),
    }
    out = _TEMPLATE
    for token, value in repl.items():
        out = out.replace(token, value)
    return out


# ---------------------------------------------------------------------------
# Drift check + safety.
# ---------------------------------------------------------------------------

def check_page(path, label: dict) -> list:
    """Parse the ON-DISK html and return human-readable drift strings.

    Compares price, buy-button href, and <title> against the label-derived
    expected values. Empty list = in sync. Never raises on a missing/odd page.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            html_text = fh.read()
    except OSError as e:
        return [f"cannot read page: {e}"]

    drift = []
    sku = str(label.get("sku") or os.path.basename(os.path.dirname(str(path))))

    # Price (the source value, e.g. $65.00).
    want_price = _price_str(label)
    m = re.search(r'<span class="item-price">([^<]*)</span>', html_text)
    have_price = m.group(1).strip() if m else None
    if have_price != want_price:
        drift.append(f"price: page has {have_price!r}, label-derived {want_price!r}")

    # Buy-button href.
    want_link = buy_link(label)
    m = re.search(r'<a href="([^"]*)" class="buy-button"', html_text)
    have_link = m.group(1) if m else None
    if have_link != want_link:
        drift.append(f"buy-link: page has {have_link!r}, label-derived {want_link!r}")

    # <title>.
    want_title = f"{seo_title(label)} | Richmond General"
    want_title_html = (_page(label).get("seo_title") and want_title) or html.escape(want_title)
    m = re.search(r"<title>(.*?)</title>", html_text, re.S)
    have_title = m.group(1).strip() if m else None
    if have_title != want_title_html:
        drift.append(f"title: page has {have_title!r}, label-derived {want_title_html!r}")

    return drift


def is_protected(html_text: str) -> bool:
    """True if the page carries a living-test or sold marker (be conservative)."""
    if not html_text:
        return False
    return any(marker in html_text for marker in _PROTECTED_MARKERS)


def _read_status(item_dir) -> dict:
    if item_dir is None:
        return {}
    p = os.path.join(str(item_dir), "status.json")
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def should_skip(label: dict, item_dir) -> bool:
    """True if the item is Sold (by label.state or a sibling status.json)."""
    if str(label.get("state") or "").strip().lower() == "sold":
        return True
    return str(_read_status(item_dir).get("status") or "").strip().lower() == "sold"


# ---------------------------------------------------------------------------
# I/O.
# ---------------------------------------------------------------------------

def _load_label(item_dir) -> dict:
    with open(os.path.join(str(item_dir), "label.json"), encoding="utf-8") as fh:
        return json.load(fh)


def would_skip(item_dir, label: dict) -> str | None:
    """Why a (non-forced) regen of this item would be skipped, or None to proceed.

    Single source of truth for the skip rules shared by ``write_page`` and the
    ``--dry-run`` path: Sold state, a protected existing page, or a sibling
    ``buy/`` redirect dir. Returns a short human-readable reason or None.
    """
    if should_skip(label, item_dir):
        return "item is Sold"
    index = os.path.join(str(item_dir), "index.html")
    if os.path.isfile(index):
        try:
            with open(index, encoding="utf-8") as fh:
                existing = fh.read()
        except OSError:
            existing = ""
        if is_protected(existing):
            return "existing page is a living-test/sold page"
    # The RG-0027 /buy/ redirect lives in a sibling dir — protect those items too.
    if os.path.isdir(os.path.join(str(item_dir), "buy")):
        return "has a /buy/ redirect layer"
    return None


def write_page(sku: str, item_dir, label: dict, force: bool = False):
    """Write items/<sku>/index.html. Returns the path, or None when skipped.

    Skips (returns None, prints why) when the item is Sold OR the existing page
    is protected, unless ``force`` is set.
    """
    index = os.path.join(str(item_dir), "index.html")

    if not force:
        reason = would_skip(item_dir, label)
        if reason:
            print(f"  - skip {sku}: {reason} (use --force to regenerate)")
            return None

    out = render_page(sku, label, item_dir)
    with open(index, "w", encoding="utf-8") as fh:
        fh.write(out)
    return index


def _all_skus():
    return sorted(
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(ROOT, "RG-*", "label.json"))
    )


def managed_skus(items: dict) -> list:
    """SKUs whose label has a truthy `page` block — the "generator-managed" set.

    ``items`` maps SKU -> parsed label dict. A page block makes an item managed
    (its prose came through the generator), so its on-disk page is expected to
    round-trip from label.json and any drift is a real failure. Legacy
    hand-curated pages have NO page block (or a non-dict / empty one) and are
    excluded, so their expected "$80 vs $80.00" / hand-title / sold-archive
    differences never false-fail the CI drift gate. Returned sorted.
    """
    return sorted(sku for sku, label in items.items() if _page(label))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate items/RG-XXXX/index.html from label.json (single source of truth)."
    )
    ap.add_argument("sku", nargs="?", help="the item SKU, e.g. RG-0055")
    ap.add_argument("--all", action="store_true", help="iterate every items/RG-*/")
    ap.add_argument("--check", action="store_true",
                    help="report drift vs label.json; exit non-zero if any page drifts")
    ap.add_argument("--managed-only", action="store_true",
                    help="with --all --check, restrict to generator-managed items "
                         "(label.json has a truthy `page` block); skip legacy "
                         "hand-curated pages so their expected differences don't fail")
    ap.add_argument("--force", action="store_true",
                    help="write even if the page is protected (living-test/sold/buy-redirect)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the first ~40 lines / a report; write nothing")
    args = ap.parse_args()

    if args.all:
        skus = _all_skus()
    elif args.sku:
        skus = [args.sku]
    else:
        ap.error("provide a SKU or --all")
        return 2

    # --check mode: compare on-disk pages to label-derived values.
    if args.check:
        # --managed-only narrows the --all set to generator-managed items (those
        # whose label.json carries a truthy `page` block), so legacy hand-curated
        # pages (no page block) don't false-fail the CI drift gate. It only
        # affects --all; a single-SKU --check still checks that SKU.
        skipped_unmanaged = 0
        if args.managed_only and args.all:
            labels = {}
            for sku in skus:
                try:
                    labels[sku] = _load_label(os.path.join(ROOT, sku))
                except (OSError, json.JSONDecodeError) as e:
                    print(f"  ! {sku}: cannot read label.json: {e}")
                    labels[sku] = {}
            managed = set(managed_skus(labels))
            skipped_unmanaged = len(skus) - len(managed)
            skus = [sku for sku in skus if sku in managed]

        any_drift = False
        drifted = 0
        for sku in skus:
            item_dir = os.path.join(ROOT, sku)
            index = os.path.join(item_dir, "index.html")
            try:
                label = _load_label(item_dir)
            except (OSError, json.JSONDecodeError) as e:
                print(f"  ! {sku}: cannot read label.json: {e}")
                any_drift = True
                drifted += 1
                continue
            if not os.path.isfile(index):
                # No page yet for a Listed/Sold item is itself a problem; for
                # others it's fine. Only flag Listed/Sold.
                if str(label.get("state") or "").strip() in ("Listed", "Sold"):
                    print(f"  ! {sku}: no index.html (Listed/Sold item)")
                    any_drift = True
                    drifted += 1
                continue
            drift = check_page(index, label)
            if drift:
                any_drift = True
                drifted += 1
                print(f"DRIFT {sku}:")
                for d in drift:
                    print(f"    - {d}")

        if args.managed_only and args.all:
            print(
                f"managed pages checked: {len(skus)}, drifted: {drifted}, "
                f"skipped (unmanaged): {skipped_unmanaged}"
            )
        if not any_drift:
            if not (args.managed_only and args.all):
                print(f"OK: {len(skus)} page(s) in sync with label.json.")
            return 0
        return 1

    # Generate (or dry-run) mode.
    rc = 0
    for sku in skus:
        item_dir = os.path.join(ROOT, sku)
        try:
            label = _load_label(item_dir)
        except (OSError, json.JSONDecodeError) as e:
            print(f"  ! {sku}: cannot read label.json: {e}")
            rc = 1
            continue

        if args.dry_run:
            # Show what WOULD happen, write nothing.
            if not args.force:
                reason = would_skip(item_dir, label)
                if reason:
                    print(f"  - {sku}: would SKIP ({reason})")
                    continue
            out = render_page(sku, label, item_dir)
            print(f"=== {sku} (dry-run, first 40 lines) ===")
            for line in out.splitlines()[:40]:
                print(line)
            print("=== (truncated; nothing written) ===")
            continue

        path = write_page(sku, item_dir, label, force=args.force)
        if path:
            print(f"  wrote {path}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
