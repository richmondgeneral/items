#!/usr/bin/env python3
"""
Build an agent-review bundle from Playwright screenshots.

Outputs:
- qa-artifacts/agent-review/manifest.json
- qa-artifacts/agent-review/review_prompt.md
- qa-artifacts/agent-review/agent_report_template.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


SHOT_RE = re.compile(r"^(desktop|mobile)-(front|back)\.png$")


@dataclass
class ScreenshotItem:
    sku: str
    viewport: str
    side: str
    relative_path: str
    absolute_path: str
    size_bytes: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build screenshot review pack.")
    parser.add_argument(
        "--screenshots-dir",
        default="qa-artifacts/screenshots",
        help="Directory containing screenshot files.",
    )
    parser.add_argument(
        "--output-dir",
        default="qa-artifacts/agent-review",
        help="Directory where review pack files are written.",
    )
    parser.add_argument(
        "--sku",
        action="append",
        default=[],
        help="Optional SKU filter (repeatable), e.g. --sku RG-0007",
    )
    return parser.parse_args()


def iter_screenshots(root: Path) -> Iterable[ScreenshotItem]:
    if not root.exists():
        return []
    items: list[ScreenshotItem] = []
    for sku_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        sku = sku_dir.name
        for shot in sorted(p for p in sku_dir.iterdir() if p.is_file()):
            match = SHOT_RE.match(shot.name)
            if not match:
                continue
            viewport, side = match.groups()
            items.append(
                ScreenshotItem(
                    sku=sku,
                    viewport=viewport,
                    side=side,
                    relative_path=str(shot),
                    absolute_path=str(shot.resolve()),
                    size_bytes=shot.stat().st_size,
                )
            )
    return items


def build_prompt(items: list[ScreenshotItem]) -> str:
    grouped: dict[str, list[ScreenshotItem]] = {}
    for item in items:
        grouped.setdefault(item.sku, []).append(item)

    lines: list[str] = []
    lines.append("# Agent Layout Review Request")
    lines.append("")
    lines.append("Review these screenshots for concrete UI/layout defects.")
    lines.append("Flag only actionable issues and include severity:")
    lines.append("- `P0`: critical defect blocking production deploy")
    lines.append("- `P1`: user flow breakage or severe layout failure")
    lines.append("- `P2`: important visual/interaction defects")
    lines.append("- `P3`: polish issues worth fixing")
    lines.append("")
    lines.append("Check for:")
    lines.append("- clipped or overlapping text/content")
    lines.append("- missing images/QR codes/buttons")
    lines.append("- broken flip-card front/back layout")
    lines.append("- mobile-specific breakage")
    lines.append("- obvious accessibility visual regressions")
    lines.append("")
    lines.append("## Required Output")
    lines.append("")
    lines.append("Write findings to `qa-artifacts/agent-review/findings.json` using this shape:")
    lines.append("")
    lines.append("```json")
    lines.append("{")
    lines.append('  "generated_at": "2026-01-01T00:00:00Z",')
    lines.append('  "reviewer": "agent-name",')
    lines.append('  "summary": "optional short summary",')
    lines.append('  "findings": [')
    lines.append("    {")
    lines.append('      "sku": "RG-0007",')
    lines.append('      "viewport": "mobile",')
    lines.append('      "side": "front",')
    lines.append('      "priority": "P2",')
    lines.append('      "title": "Buy button overlaps card edge",')
    lines.append('      "description": "On mobile front view, the Buy button clips against the right edge.",')
    lines.append('      "screenshot": "/absolute/path/to/qa-artifacts/screenshots/RG-0007/mobile-front.png"')
    lines.append("    }")
    lines.append("  ]")
    lines.append("}")
    lines.append("```")
    lines.append("")
    lines.append("## Screenshot Index")
    lines.append("")

    for sku in sorted(grouped.keys()):
        lines.append(f"### {sku}")
        for item in sorted(grouped[sku], key=lambda s: (s.viewport, s.side)):
            label = f"{item.viewport} {item.side}"
            lines.append(f"- `{label}`: `{item.absolute_path}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    screenshots_dir = Path(args.screenshots_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    items = list(iter_screenshots(screenshots_dir))
    if args.sku:
        allowed = set(args.sku)
        items = [item for item in items if item.sku in allowed]

    if not items:
        raise SystemExit(
            "No screenshots found. Run `npm run ui:test` before building the review pack."
        )

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "workspace": str(Path.cwd().resolve()),
        "screenshots_dir": str(screenshots_dir.resolve()),
        "count": len(items),
        "items": [asdict(item) for item in items],
    }

    manifest_path = output_dir / "manifest.json"
    prompt_path = output_dir / "review_prompt.md"
    template_path = output_dir / "agent_report_template.json"

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    prompt_path.write_text(build_prompt(items), encoding="utf-8")
    template = {
        "generated_at": datetime.now(UTC).isoformat(),
        "reviewer": "agent-name",
        "summary": "",
        "findings": [],
    }
    template_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {manifest_path}")
    print(f"Wrote {prompt_path}")
    print(f"Wrote {template_path}")
    print(f"Screenshots indexed: {len(items)}")


if __name__ == "__main__":
    main()
