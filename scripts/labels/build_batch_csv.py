#!/usr/bin/env python3
"""
Build batch label CSV from per-item RG-*/label.json files.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


SKU_RE = re.compile(r"^RG-\d{4}$")
REQUIRED_FIELDS = (
    "sku",
    "product_name",
    "attributes",
    "price",
    "condition",
    "condition_notes",
    "qr_code_url",
)
CSV_COLUMNS = (
    "Product Name",
    "Attributes",
    "Price",
    "Condition",
    "Condition Notes",
    "SKU",
    "QR Code URL",
)


class LabelError(Exception):
    pass


@dataclass(frozen=True)
class LabelRecord:
    sku: str
    product_name: str
    attributes: str
    price: str
    condition: str
    condition_notes: str
    qr_code_url: str

    def to_csv_row(self) -> dict[str, str]:
        return {
            "Product Name": self.product_name,
            "Attributes": self.attributes,
            "Price": self.price,
            "Condition": self.condition,
            "Condition Notes": self.condition_notes,
            "SKU": self.sku,
            "QR Code URL": self.qr_code_url,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build rg-labels-batch.csv from RG-*/label.json files."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing RG-* directories.",
    )
    parser.add_argument(
        "--output",
        default="qa-artifacts/labels/rg-labels-batch.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--sku",
        action="append",
        default=[],
        help="Optional SKU filter (repeatable), e.g. --sku RG-0007",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Skip missing label.json files instead of failing.",
    )
    return parser.parse_args()


def discover_skus(root: Path) -> list[str]:
    return sorted(
        entry.name
        for entry in root.iterdir()
        if entry.is_dir() and SKU_RE.match(entry.name)
    )


def as_nonempty_str(payload: dict[str, object], field: str, *, allow_empty: bool = False) -> str:
    value = payload.get(field)
    if not isinstance(value, str):
        raise LabelError(f"Field '{field}' must be a string.")
    stripped = value.strip()
    if not stripped and not allow_empty:
        raise LabelError(f"Field '{field}' must not be empty.")
    return stripped


def normalize_price(raw: str) -> str:
    cleaned = raw.replace("$", "").strip()
    try:
        return f"{float(cleaned):.2f}"
    except ValueError as exc:
        raise LabelError(f"Invalid price value: {raw!r}") from exc


def load_label(label_path: Path, expected_sku: str) -> LabelRecord:
    try:
        payload = json.loads(label_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LabelError(f"Invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise LabelError("Root JSON value must be an object.")

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise LabelError(f"Missing required field(s): {', '.join(missing)}.")

    sku = as_nonempty_str(payload, "sku")
    if sku != expected_sku:
        raise LabelError(f"Field 'sku' ({sku}) does not match folder ({expected_sku}).")
    if not SKU_RE.match(sku):
        raise LabelError(f"Field 'sku' is invalid: {sku}.")

    qr_code_url = as_nonempty_str(payload, "qr_code_url")
    if not qr_code_url.startswith("http://") and not qr_code_url.startswith("https://"):
        raise LabelError("Field 'qr_code_url' must be an absolute URL.")

    return LabelRecord(
        sku=sku,
        product_name=as_nonempty_str(payload, "product_name"),
        attributes=as_nonempty_str(payload, "attributes"),
        price=normalize_price(as_nonempty_str(payload, "price")),
        condition=as_nonempty_str(payload, "condition"),
        condition_notes=as_nonempty_str(payload, "condition_notes", allow_empty=True),
        qr_code_url=qr_code_url,
    )


def sku_sort_key(sku: str) -> tuple[str, int]:
    return (sku[:3], int(sku[3:]))


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    output_path = Path(args.output).resolve()

    selected = set(args.sku)
    invalid = sorted(sku for sku in selected if not SKU_RE.match(sku))
    if invalid:
        raise SystemExit(f"Invalid --sku value(s): {', '.join(invalid)}")

    records: list[LabelRecord] = []
    skipped: list[str] = []

    for sku in discover_skus(root):
        if selected and sku not in selected:
            continue
        label_path = root / sku / "label.json"
        if not label_path.exists():
            if args.allow_missing:
                skipped.append(sku)
                continue
            raise SystemExit(f"Missing required label file: {label_path}")

        try:
            records.append(load_label(label_path, sku))
        except LabelError as exc:
            raise SystemExit(f"{label_path}: {exc}") from exc

    records.sort(key=lambda row: sku_sort_key(row.sku))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_COLUMNS))
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_csv_row())

    print(f"Wrote {output_path}")
    print(f"Records: {len(records)}")
    if skipped:
        print(f"Skipped missing labels ({len(skipped)}): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
