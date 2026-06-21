"""Tests for build_item_page.py — the deterministic item-page generator.

label.json is the single source of truth: structured fields (price, links,
image, dims, era, QR, fulfillment) are ALWAYS derived from it (kills drift).
Curated prose lives in an optional `page` block, with mechanical fallbacks.
"""
import json
import pathlib

import build_item_page as bip

ITEMS = pathlib.Path(__file__).resolve().parents[2]  # the items/ repo root
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def minimal_label():
    """A small in-memory label exercising the structured-field derivations.

    Mirrors RG-0055's shape (em-dash product_name, bulleted attributes, an
    estimates block with circa + diameter dims, a Square buy_link, qr-buy),
    so the derived title/era/dims/details/buy-link/QR are all predictable.
    """
    return {
        "sku": "RG-0055",
        "product_name": "Widget Title — Long Descriptive Tail (Size 50)",
        "attributes": "Maker X • LARGE thing • 18in tall × 12.5in dia • extra seg • dropped seg",
        "price": "65.00",
        "condition": "Antique — honest as-found; heavy patina; complete",
        "condition_notes": (
            "A substantial antique vessel at 18 in tall by 12.5 in diameter with a "
            "hinged lid and a wire bail handle. It wears its age honestly with a dark "
            "patina and surface rust. Sold as found."
        ),
        "state": "Listed",
        "fulfillment": "local_pickup_only",
        "channels": {
            "square": {"buy_link": "https://square.link/u/qhpAeEXd"},
        },
        "qr_codes": {"buy": {"file": "qr-buy.png"}},
        "identity": {"maker": "Kreamer", "maker_location": "Brooklyn, NY"},
        "estimates": {
            "circa": {"value": "c. 1936-1945", "est": True},
            "dimensions_in": {"height": 18, "diameter": 12.5},
        },
        "photos": {"hero": "hero.jpeg", "cutout": "cutout.png"},
    }


# ---------------------------------------------------------------------------
# 1. Content — render_page fills the RG-0055 template from a label.
# ---------------------------------------------------------------------------

def test_render_page_contains_derived_structured_fields():
    label = minimal_label()
    html = bip.render_page("RG-0055", label)

    # Title: seo_title falls back to card_title -> "Widget Title".
    assert "<title>Widget Title | Richmond General</title>" in html
    # Price kept as two-decimals in the source (view-time JS strips .00).
    assert "$65.00" in html
    # Buy button href derived from channels.square.buy_link.
    assert 'href="https://square.link/u/qhpAeEXd" class="buy-button"' in html
    # og:image = absolute GitHub Pages URL of the cutout.
    assert (
        'og:image" content="https://richmondgeneral.github.io/items/RG-0055/cutout.png"'
        in html
    )
    # QR uses qr-buy.png.
    assert 'src="./qr-buy.png"' in html
    # SKU badge text.
    assert '<span class="sku-badge">RG-0055</span>' in html
    # Main image is the cutout, relative.
    assert 'src="./cutout.png"' in html


def test_render_page_contains_four_derived_detail_values():
    label = minimal_label()
    html = bip.render_page("RG-0055", label)
    # Maker = identity.maker + ", {location}".
    assert "Kreamer (Brooklyn, NY)" in html or "Kreamer, Brooklyn, NY" in html
    # Era = circa.value + " (est.)" because est is truthy.
    assert "c. 1936-1945 (est.)" in html
    # Dimensions = height + diameter form.
    assert "18&Prime; H &times; 12.5&Prime; dia" in html
    # Condition = first clause of `condition`.
    assert "Antique" in html
    # The detail labels are present (it's a details grid).
    for lbl in ("Maker", "Era", "Dimensions", "Condition"):
        assert f"<p class=\"detail-label\">{lbl}</p>" in html


def test_render_page_preserves_trailing_scripts():
    html = bip.render_page("RG-0055", minimal_label())
    # The flip handler and the .00-stripping price formatter must survive verbatim.
    assert "fc.classList.toggle('flipped')" in html
    assert r"/\$([0-9]+)\.00\b/g" in html


# ---------------------------------------------------------------------------
# 2. Fallbacks vs. curated page block.
# ---------------------------------------------------------------------------

def test_fallbacks_when_no_page_block():
    label = minimal_label()
    # card_title <- product_name pre em-dash.
    assert bip.card_title(label) == "Widget Title"
    # story <- condition_notes verbatim.
    assert bip.story(label) == label["condition_notes"]
    # era_line <- first <=3 attribute segments joined by ' • '.
    assert bip.era_line(label) == "Maker X • LARGE thing • 18in tall × 12.5in dia"
    # seo_title <- card_title.
    assert bip.seo_title(label) == "Widget Title"
    # seo_description <- condition_notes truncated ~155 chars at a word boundary.
    desc = bip.seo_description(label)
    assert len(desc) <= 160
    assert desc and not desc.endswith(" ")
    assert label["condition_notes"].startswith(desc.rstrip(" .")[:20])


def test_curated_page_block_wins_and_entities_survive():
    label = minimal_label()
    label["page"] = {
        "seo_title": "Curated SEO Title",
        "seo_description": "Curated description with an &mdash; entity.",
        "card_title": "Curated Card Title &amp; More",
        "era_line": "Era &bull; Line &ndash; curated",
        "story": "Curated story with &rsquo;quotes&rsquo; and &Prime; marks.",
        "details": {"Maker": "Curated &amp; Co.", "Era": "1900", "Dimensions": "X", "Condition": "Mint"},
    }
    assert bip.card_title(label) == "Curated Card Title &amp; More"
    assert bip.era_line(label) == "Era &bull; Line &ndash; curated"
    assert bip.story(label) == "Curated story with &rsquo;quotes&rsquo; and &Prime; marks."
    assert bip.seo_title(label) == "Curated SEO Title"
    assert bip.seo_description(label) == "Curated description with an &mdash; entity."

    html = bip.render_page("RG-0055", label)
    # Curated entities must be inserted AS-IS (trusted), not double-escaped.
    assert "Curated Card Title &amp; More" in html
    assert "&amp;amp;" not in html  # no double-escaping of curated content
    assert "Curated story with &rsquo;quotes&rsquo;" in html
    assert "<title>Curated SEO Title | Richmond General</title>" in html
    # Curated details win.
    assert "Curated &amp; Co." in html


def test_mechanical_fallback_text_is_html_escaped():
    label = minimal_label()
    # Inject an angle-bracket into the mechanically-derived path.
    label["product_name"] = "Title <script> — tail"
    html = bip.render_page("RG-0055", label)
    # Derived (untrusted) text must be escaped.
    assert "&lt;script&gt;" in html
    assert "<script> —" not in html.split("</style>")[1]  # not raw in body


# ---------------------------------------------------------------------------
# Pure-helper unit tests (load-bearing derivations).
# ---------------------------------------------------------------------------

def test_dims_str_diameter_form():
    assert bip.dims_str({"height": 18, "diameter": 12.5}) == "18&Prime; H &times; 12.5&Prime; dia"


def test_dims_str_hwd_form():
    assert bip.dims_str({"height": 10, "width": 8, "depth": 4}) == "10 &times; 8 &times; 4 in"


def test_dims_str_empty():
    assert bip.dims_str({}) == ""


def test_qr_buy_file_prefers_label(tmp_path):
    label = {"qr_codes": {"buy": {"file": "custom-qr.png"}}}
    assert bip.qr_buy_file("RG-0001", label, tmp_path) == "custom-qr.png"


def test_qr_buy_file_falls_back_to_existing_file(tmp_path):
    (tmp_path / "qr-buy.png").write_bytes(b"x")
    assert bip.qr_buy_file("RG-0001", {}, tmp_path) == "qr-buy.png"


def test_qr_buy_file_final_fallback(tmp_path):
    assert bip.qr_buy_file("RG-0001", {}, tmp_path) == "qr-code.png"


def test_main_image_prefers_cutout():
    assert bip.main_image("RG-0001", {"photos": {"cutout": "cutout.png", "hero": "hero.jpeg"}}) == "./cutout.png"


def test_main_image_hero_fallback():
    assert bip.main_image("RG-0001", {"photos": {"hero": "hero.jpeg"}}) == "./hero.jpeg"


def test_main_image_final_fallback():
    assert bip.main_image("RG-0001", {}) == "./hero.jpeg"


def test_buy_link_present():
    assert bip.buy_link({"channels": {"square": {"buy_link": "https://square.link/u/x"}}}) == "https://square.link/u/x"


def test_buy_link_missing_is_hash():
    assert bip.buy_link({}) == "#"


def test_fulfillment_local_pickup_via_field():
    assert bip.fulfillment_line({"fulfillment": "local_pickup_only"}) == "Local pickup only"


def test_fulfillment_local_pickup_via_shipping():
    assert bip.fulfillment_line({"shipping": {"local_pickup_only": True}}) == "Local pickup only"


def test_fulfillment_ships_default():
    assert bip.fulfillment_line({}) == "Ships or local pickup"


# ---------------------------------------------------------------------------
# 3. --check drift detection.
# ---------------------------------------------------------------------------

def test_check_page_in_sync(tmp_path):
    label = minimal_label()
    p = tmp_path / "index.html"
    p.write_text(bip.render_page("RG-0055", label), encoding="utf-8")
    assert bip.check_page(p, label) == []


def test_check_page_detects_drift(tmp_path):
    label = minimal_label()
    html = bip.render_page("RG-0055", label)
    # Corrupt the on-disk page: wrong price, wrong buy-link, wrong title.
    html = html.replace("$65.00", "$45.00")
    html = html.replace("https://square.link/u/qhpAeEXd", "https://square.link/u/WRONG")
    html = html.replace("<title>Widget Title | Richmond General</title>",
                        "<title>Stale Title | Richmond General</title>")
    p = tmp_path / "index.html"
    p.write_text(html, encoding="utf-8")
    drift = bip.check_page(p, label)
    assert drift  # non-empty
    joined = " ".join(drift).lower()
    assert "price" in joined
    assert "buy" in joined or "link" in joined
    assert "title" in joined


# ---------------------------------------------------------------------------
# 4. Safety: is_protected / should_skip.
# ---------------------------------------------------------------------------

def test_is_protected_variant_stack():
    assert bip.is_protected('<div class="variant-stack" data-mode="slider">') is True


def test_is_protected_tilt_motion():
    # The TILT / iridescent living-test markers.
    assert bip.is_protected('<div class="card-front" data-finish="iridescent">') is True
    assert bip.is_protected("IRIDESCENT FOIL CONTROLLER") is True


def test_is_protected_buy_redirect():
    assert bip.is_protected("BUY REDIRECT LAYER") is True


def test_is_protected_sold_markers():
    assert bip.is_protected('<div class="sold-status-panel">') is True
    assert bip.is_protected('<a class="item-card" data-status="sold">') is True
    assert bip.is_protected('<span class="sku-badge sold-badge">RG-0002 · SOLD</span>') is True


def test_is_protected_false_for_plain_page():
    html = bip.render_page("RG-0055", minimal_label())
    assert bip.is_protected(html) is False


def test_should_skip_state_sold():
    assert bip.should_skip({"state": "Sold"}, None) is True


def test_should_skip_listed_not_skipped(tmp_path):
    assert bip.should_skip({"state": "Listed"}, tmp_path) is False


def test_should_skip_status_json_sold(tmp_path):
    (tmp_path / "status.json").write_text(json.dumps({"status": "sold"}), encoding="utf-8")
    assert bip.should_skip({"state": "Listed"}, tmp_path) is True


# ---------------------------------------------------------------------------
# Graceful degradation on a minimal old-schema label.
# ---------------------------------------------------------------------------

def test_render_page_minimal_old_schema_does_not_throw():
    old = {
        "sku": "RG-0001",
        "product_name": "Little Orphan Annie Comic Strip Book",
        "attributes": "Vintage Book • Harold Gray • 1930s",
        "price": "19.50",
        "condition": "VG",
        "condition_notes": "Light wear spine intact",
    }
    html = bip.render_page("RG-0001", old)
    assert "<title>Little Orphan Annie Comic Strip Book | Richmond General</title>" in html
    assert "$19.50" in html
    # No buy link -> '#'.
    assert 'href="#" class="buy-button"' in html
    # No cutout/hero -> hero.jpeg default in og + img.
    assert "https://richmondgeneral.github.io/items/RG-0001/hero.jpeg" in html


# ---------------------------------------------------------------------------
# Golden regression — RG-0055 round-trips byte-for-byte to the frozen fixture.
# ---------------------------------------------------------------------------

def test_rg0055_matches_golden_fixture():
    fixture = FIXTURES / "RG-0055.expected.html"
    if not fixture.exists():
        import pytest
        pytest.skip("golden fixture not yet frozen (A3)")
    label = json.loads((ITEMS / "RG-0055" / "label.json").read_text(encoding="utf-8"))
    got = bip.render_page("RG-0055", label, ITEMS / "RG-0055")
    assert got == fixture.read_text(encoding="utf-8")
