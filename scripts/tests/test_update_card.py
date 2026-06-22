"""Tests for build_gallery.py's targeted in-place card updater (--update-card).

These exercise update_card / _card_span against the REAL items/index.html so the
byte-preserve invariant is verified against production data: re-rendering ONE
card from its label.json must leave every OTHER card byte-for-byte identical
(only the single #item-count number from recount() may move).
"""
import os
import re

import build_gallery as bg

INDEX = bg.INDEX


def _read_index():
    return open(INDEX, encoding="utf-8").read()


def _target_sku(text):
    """Lowest carded SKU in the real gallery (asserts at least one exists)."""
    carded = bg.carded_skus(text)
    assert carded, "expected at least one carded SKU in the real index.html"
    return sorted(carded)[0]


def _spans(text):
    """sku -> (start, end) char span of each card block, via _card_span."""
    return {sku: bg._card_span(text, sku) for sku in bg.carded_skus(text)}


def test_card_span_matches_exactly_one_card():
    text = _read_index()
    sku = _target_sku(text)
    span = bg._card_span(text, sku)
    assert span is not None
    block = text[span[0]:span[1]]
    # The span runs from the comment line through exactly ONE closing </a>.
    assert block.startswith(f"            <!-- {sku}:")
    assert block.endswith("</a>")
    assert block.count("<a href=") == 1
    assert block.count("</a>") == 1


def test_card_span_none_for_uncarded_sku():
    text = _read_index()
    # A SKU that is not in the gallery at all.
    assert "RG-9999" not in bg.carded_skus(text)
    assert bg._card_span(text, "RG-9999") is None


def test_update_card_rerenders_target_and_preserves_others():
    text = _read_index()
    sku = _target_sku(text)

    items = bg.load_items()
    assert sku in items, f"{sku} carded but absent from label set"

    # Capture every OTHER card's exact bytes BEFORE the update.
    before_spans = _spans(text)
    others_before = {
        s: text[sp[0]:sp[1]]
        for s, sp in before_spans.items()
        if s != sku and sp is not None
    }

    # Set a sentinel price on the target's label, then re-render its card.
    sentinel = "$1,234"
    items[sku]["price"] = sentinel

    new_text, changed = bg.update_card(text, sku, items)
    assert changed is True

    # (a) the updated card now carries the sentinel price.
    new_span = bg._card_span(new_text, sku)
    assert new_span is not None
    new_block = new_text[new_span[0]:new_span[1]]
    assert sentinel in new_block

    # (b) every OTHER card is byte-identical.
    after_spans = _spans(new_text)
    assert set(after_spans) == set(before_spans), "card set changed"
    for s, exact in others_before.items():
        sp = after_spans[s]
        assert sp is not None, f"{s} card vanished"
        assert new_text[sp[0]:sp[1]] == exact, f"{s} card changed unexpectedly"

    # (c) the ONLY non-card delta is recount()'s single #item-count number:
    # blanking the count in both texts makes them identical.
    blank = lambda t: re.sub(
        r'(<div class="stat-number" id="item-count">)\d*(</div>)', r"\1\2", t
    )
    # Remove the target card region from both (its content legitimately changed),
    # then assert the rest of the document is unchanged save the count.
    ob = before_spans[sku]
    nb = new_span
    old_rest = blank(text[:ob[0]] + text[ob[1]:])
    new_rest = blank(new_text[:nb[0]] + new_text[nb[1]:])
    assert old_rest == new_rest


def test_update_card_noop_for_missing_sku():
    text = _read_index()
    items = bg.load_items()
    # A SKU not present anywhere -> no card, not in items -> unchanged.
    new_text, changed = bg.update_card(text, "RG-9999", items)
    assert changed is False
    assert new_text == text


def test_update_card_noop_when_item_absent_from_labels():
    """Carded SKU but absent from the label set -> no-op (can't re-render)."""
    text = _read_index()
    sku = _target_sku(text)
    new_text, changed = bg.update_card(text, sku, {})  # empty label set
    assert changed is False
    assert new_text == text
