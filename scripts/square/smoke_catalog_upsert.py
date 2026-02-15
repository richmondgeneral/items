#!/usr/bin/env python3
"""Square Catalog write-path smoke test.

Creates a temporary ITEM via upsertCatalogObject, verifies response, then deletes it.
Writes request/response logs under qa-artifacts/square-smoke.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

API_BASE = "https://connect.squareup.com/v2"
DEFAULT_API_VERSION = os.getenv("SQUARE_API_VERSION", "2025-10-16")


@dataclass
class SmokeResult:
    success: bool
    api_version: str
    run_dir: str
    item_id: Optional[str]
    cleanup_deleted: Optional[bool]
    idempotency_key: str
    create_status: int
    cleanup_status: Optional[int]
    error: Optional[str] = None


def utc_now_token() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def resolve_token() -> str:
    token = os.getenv("SQUARE_ACCESS_TOKEN") or os.getenv("SQUARE_TOKEN")
    if not token:
        raise RuntimeError("Set SQUARE_ACCESS_TOKEN (or SQUARE_TOKEN) before running this smoke test.")
    return token


def make_headers(token: str, api_version: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Square-Version": api_version,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def build_upsert_payload(name_prefix: str) -> Tuple[Dict[str, Any], str]:
    run_id = uuid.uuid4().hex[:10]
    idempotency_key = f"smoke-upsert-{utc_now_token()}-{run_id}"
    temp_item_id = f"#SMOKE_ITEM_{run_id.upper()}"
    temp_var_id = f"#SMOKE_VAR_{run_id.upper()}"

    payload = {
        "idempotency_key": idempotency_key,
        "object": {
            "type": "ITEM",
            "id": temp_item_id,
            "item_data": {
                "name": f"{name_prefix} {utc_now_token()}",
                "description": "Temporary object for catalog upsert smoke test. Safe to delete.",
                "variations": [
                    {
                        "type": "ITEM_VARIATION",
                        "id": temp_var_id,
                        "item_variation_data": {
                            "name": "Smoke Variation",
                            "pricing_type": "FIXED_PRICING",
                            "price_money": {
                                "amount": 100,
                                "currency": "USD",
                            },
                            "track_inventory": False,
                        },
                    }
                ],
            },
        },
    }

    return payload, idempotency_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Square Catalog upsert smoke test")
    parser.add_argument(
        "--api-version",
        default=DEFAULT_API_VERSION,
        help=f"Square API version header (default: {DEFAULT_API_VERSION})",
    )
    parser.add_argument(
        "--name-prefix",
        default="RG Smoke Test",
        help="Prefix for temporary test item name",
    )
    parser.add_argument(
        "--log-root",
        default="qa-artifacts/square-smoke",
        help="Directory to write request/response logs",
    )
    parser.add_argument(
        "--keep-object",
        action="store_true",
        help="Skip cleanup delete (keeps temp object in catalog)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout seconds (default: 30)",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    run_token = utc_now_token()
    run_dir = Path(args.log_root) / run_token
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        token = resolve_token()
    except RuntimeError as exc:
        if args.json:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": str(exc),
                    },
                    indent=2,
                )
            )
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    headers = make_headers(token, args.api_version)
    payload, idempotency_key = build_upsert_payload(args.name_prefix)

    request_log = {
        "request": {
            "method": "POST",
            "url": f"{API_BASE}/catalog/object",
            "headers": {
                "Square-Version": args.api_version,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer ***redacted***",
            },
            "body": payload,
        }
    }
    write_json(run_dir / "create.request.json", request_log)

    create_status = 0
    cleanup_status: Optional[int] = None
    cleanup_deleted: Optional[bool] = None
    item_id: Optional[str] = None

    try:
        create_resp = requests.post(
            f"{API_BASE}/catalog/object",
            headers=headers,
            json=payload,
            timeout=args.timeout,
        )
        create_status = create_resp.status_code
        create_data = create_resp.json() if create_resp.content else {}
    except Exception as exc:
        result = SmokeResult(
            success=False,
            api_version=args.api_version,
            run_dir=str(run_dir),
            item_id=None,
            cleanup_deleted=None,
            idempotency_key=idempotency_key,
            create_status=create_status,
            cleanup_status=None,
            error=f"Create request failed: {exc}",
        )
        write_json(run_dir / "create.response.json", {"error": str(exc)})
        if args.json:
            print(json.dumps(result.__dict__, indent=2))
        else:
            print(result.error, file=sys.stderr)
        return 1

    write_json(
        run_dir / "create.response.json",
        {
            "status_code": create_status,
            "body": create_data,
        },
    )

    if create_status // 100 != 2:
        errors = create_data.get("errors") if isinstance(create_data, dict) else None
        result = SmokeResult(
            success=False,
            api_version=args.api_version,
            run_dir=str(run_dir),
            item_id=None,
            cleanup_deleted=None,
            idempotency_key=idempotency_key,
            create_status=create_status,
            cleanup_status=None,
            error=f"Create failed with HTTP {create_status}: {errors}",
        )
        if args.json:
            print(json.dumps(result.__dict__, indent=2))
        else:
            print(result.error, file=sys.stderr)
        return 1

    catalog_object = create_data.get("catalog_object", {})
    item_id = catalog_object.get("id")
    if not item_id:
        result = SmokeResult(
            success=False,
            api_version=args.api_version,
            run_dir=str(run_dir),
            item_id=None,
            cleanup_deleted=None,
            idempotency_key=idempotency_key,
            create_status=create_status,
            cleanup_status=None,
            error="Create response missing catalog_object.id",
        )
        if args.json:
            print(json.dumps(result.__dict__, indent=2))
        else:
            print(result.error, file=sys.stderr)
        return 1

    if args.keep_object:
        cleanup_deleted = False
    else:
        delete_headers = {
            "Authorization": headers["Authorization"],
            "Square-Version": headers["Square-Version"],
            "Accept": "application/json",
        }
        delete_url = f"{API_BASE}/catalog/object/{item_id}"

        write_json(
            run_dir / "cleanup.request.json",
            {
                "request": {
                    "method": "DELETE",
                    "url": delete_url,
                    "headers": {
                        "Square-Version": args.api_version,
                        "Accept": "application/json",
                        "Authorization": "Bearer ***redacted***",
                    },
                }
            },
        )

        try:
            delete_resp = requests.delete(delete_url, headers=delete_headers, timeout=args.timeout)
            cleanup_status = delete_resp.status_code
            delete_data = delete_resp.json() if delete_resp.content else {}
        except Exception as exc:
            cleanup_status = None
            delete_data = {"error": str(exc)}

        write_json(
            run_dir / "cleanup.response.json",
            {
                "status_code": cleanup_status,
                "body": delete_data,
            },
        )

        cleanup_deleted = cleanup_status is not None and cleanup_status // 100 == 2

    success = cleanup_deleted is not False or args.keep_object
    if not args.keep_object:
        success = success and bool(cleanup_deleted)

    result = SmokeResult(
        success=success,
        api_version=args.api_version,
        run_dir=str(run_dir),
        item_id=item_id,
        cleanup_deleted=cleanup_deleted,
        idempotency_key=idempotency_key,
        create_status=create_status,
        cleanup_status=cleanup_status,
        error=None if success else "Cleanup delete failed; see cleanup.response.json",
    )

    if args.json:
        print(json.dumps(result.__dict__, indent=2))
    else:
        print(f"Square smoke: {'PASS' if result.success else 'FAIL'}")
        print(f"API version: {result.api_version}")
        print(f"Idempotency key: {result.idempotency_key}")
        print(f"Created item id: {result.item_id}")
        print(f"Create status: {result.create_status}")
        if args.keep_object:
            print("Cleanup: skipped (--keep-object)")
        else:
            print(f"Cleanup status: {result.cleanup_status}")
            print(f"Cleanup deleted: {result.cleanup_deleted}")
        print(f"Logs: {result.run_dir}")
        if result.error:
            print(f"Error: {result.error}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
