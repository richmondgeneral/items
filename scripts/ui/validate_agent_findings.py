#!/usr/bin/env python3
"""
Validate screenshot findings produced by an agent.

Inputs:
- qa-artifacts/agent-review/manifest.json
- qa-artifacts/agent-review/findings.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


SKU_RE = re.compile(r"^RG-\d{4}$")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


class ValidationError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate agent screenshot findings.")
    parser.add_argument(
        "--manifest",
        default="qa-artifacts/agent-review/manifest.json",
        help="Path to screenshot manifest JSON.",
    )
    parser.add_argument(
        "--findings",
        default="qa-artifacts/agent-review/findings.json",
        help="Path to agent findings JSON.",
    )
    parser.add_argument(
        "--fail-on",
        default="P1",
        choices=["none", "P0", "P1", "P2", "P3"],
        help="Exit non-zero if findings are this priority or higher. Use 'none' to disable severity gate.",
    )
    return parser.parse_args()


def load_json(path: Path) -> object:
    if not path.exists():
        raise ValidationError(f"Missing file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc


def validate_manifest(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValidationError("Manifest root must be a JSON object.")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValidationError("Manifest must contain an 'items' array.")
    return payload


def get_manifest_index(manifest: dict[str, object]) -> tuple[set[tuple[str, str, str]], set[str]]:
    entries = manifest.get("items", [])
    assert isinstance(entries, list)
    by_triplet: set[tuple[str, str, str]] = set()
    by_path: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        sku = entry.get("sku")
        viewport = entry.get("viewport")
        side = entry.get("side")
        absolute_path = entry.get("absolute_path")
        if isinstance(sku, str) and isinstance(viewport, str) and isinstance(side, str):
            by_triplet.add((sku, viewport, side))
        if isinstance(absolute_path, str):
            by_path.add(absolute_path)
    return by_triplet, by_path


def validate_findings(
    payload: object,
    manifest_triplets: set[tuple[str, str, str]],
    manifest_paths: set[str],
) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        raise ValidationError("Findings root must be a JSON object.")

    findings = payload.get("findings")
    if not isinstance(findings, list):
        raise ValidationError("Findings payload must include a 'findings' array.")

    normalized: list[dict[str, str]] = []
    for idx, finding in enumerate(findings):
        prefix = f"findings[{idx}]"
        if not isinstance(finding, dict):
            raise ValidationError(f"{prefix} must be an object.")

        sku = finding.get("sku")
        viewport = finding.get("viewport")
        side = finding.get("side")
        priority = finding.get("priority")
        title = finding.get("title")
        description = finding.get("description")
        screenshot = finding.get("screenshot")

        if not isinstance(sku, str) or not SKU_RE.match(sku):
            raise ValidationError(f"{prefix}.sku must match RG-XXXX.")
        if viewport not in {"desktop", "mobile"}:
            raise ValidationError(f"{prefix}.viewport must be 'desktop' or 'mobile'.")
        if side not in {"front", "back"}:
            raise ValidationError(f"{prefix}.side must be 'front' or 'back'.")
        if priority not in PRIORITY_ORDER:
            raise ValidationError(f"{prefix}.priority must be one of {sorted(PRIORITY_ORDER)}.")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError(f"{prefix}.title must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValidationError(f"{prefix}.description must be a non-empty string.")
        if not isinstance(screenshot, str) or not screenshot.strip():
            raise ValidationError(f"{prefix}.screenshot must be a non-empty string.")

        triplet = (sku, viewport, side)
        if triplet not in manifest_triplets:
            raise ValidationError(
                f"{prefix} references screenshot tuple not in manifest: {triplet}."
            )

        screenshot_path = str(Path(screenshot).resolve())
        if screenshot_path not in manifest_paths:
            raise ValidationError(
                f"{prefix}.screenshot does not match any absolute_path in manifest: {screenshot}"
            )

        normalized.append(
            {
                "sku": sku,
                "viewport": viewport,
                "side": side,
                "priority": priority,
                "title": title.strip(),
                "description": description.strip(),
                "screenshot": screenshot_path,
            }
        )

    return normalized


def enforce_threshold(findings: list[dict[str, str]], fail_on: str) -> None:
    if fail_on == "none":
        return
    threshold = PRIORITY_ORDER[fail_on]
    blockers = [f for f in findings if PRIORITY_ORDER[f["priority"]] <= threshold]
    if blockers:
        raise ValidationError(
            f"Severity gate failed: {len(blockers)} finding(s) at {fail_on} or higher."
        )


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    findings_path = Path(args.findings)

    manifest_payload = validate_manifest(load_json(manifest_path))
    manifest_triplets, manifest_paths = get_manifest_index(manifest_payload)
    findings_payload = load_json(findings_path)
    findings = validate_findings(findings_payload, manifest_triplets, manifest_paths)

    counts = Counter(f["priority"] for f in findings)
    print(f"Validated findings: {len(findings)}")
    print(
        "Priority counts:"
        f" P0={counts.get('P0', 0)}"
        f" P1={counts.get('P1', 0)}"
        f" P2={counts.get('P2', 0)}"
        f" P3={counts.get('P3', 0)}"
    )

    enforce_threshold(findings, args.fail_on)
    print(f"Severity gate passed (fail-on={args.fail_on}).")


if __name__ == "__main__":
    try:
        main()
    except ValidationError as exc:
        raise SystemExit(f"Validation failed: {exc}")
