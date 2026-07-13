"""
TradePilot AI backend audit.
"""

from __future__ import annotations

import compileall
import sys
from collections import Counter
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import main


def check_compilation() -> bool:
    print("\n[1] Compiling backend...")

    success = compileall.compile_dir(
        str(BACKEND_ROOT),
        quiet=1,
        force=False,
    )

    print(
        "PASS: Python compilation succeeded."
        if success
        else "FAIL: Python compilation errors detected."
    )

    return success


def check_routes() -> bool:
    print("\n[2] Auditing FastAPI routes...")

    schema = main.app.openapi()
    paths = schema.get("paths", {})

    route_entries = []

    for path, operations in paths.items():
        for method in operations:
            if method.lower() in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
            }:
                route_entries.append(
                    (
                        method.upper(),
                        path,
                    )
                )

    counts = Counter(route_entries)

    duplicates = {
        route: count
        for route, count in counts.items()
        if count > 1
    }

    if duplicates:
        print("FAIL: Duplicate routes detected:")

        for (method, path), count in duplicates.items():
            print(
                f"  {method} {path} registered {count} times"
            )

        return False

    print(
        f"PASS: {len(route_entries)} API operations "
        "registered without duplicates."
    )

    for method, path in sorted(
        route_entries,
        key=lambda item: (
            item[1],
            item[0],
        ),
    ):
        print(f"  {method:<8} {path}")

    return True


def check_openapi() -> bool:
    print("\n[3] Generating OpenAPI schema...")

    schema = main.app.openapi()
    paths = schema.get("paths", {})

    required_paths = {
        "/api/v1/analytics/dashboard",
        "/api/v1/analytics/analysis",
        "/api/v1/ai/chat",
        "/api/v1/coach",
        "/api/v1/reports/weekly",
        "/api/v1/reports/monthly",
        "/api/v1/trades/{trade_id}/review",
    }

    missing = sorted(
        required_paths.difference(paths)
    )

    if missing:
        print("FAIL: Required endpoints are missing:")

        for path in missing:
            print(f"  {path}")

        return False

    print(
        f"PASS: OpenAPI schema generated with "
        f"{len(paths)} documented paths."
    )

    return True


def main_audit() -> int:
    results = [
        check_compilation(),
        check_routes(),
        check_openapi(),
    ]

    print("\n" + "=" * 60)

    if all(results):
        print("BACKEND AUDIT PASSED")
        return 0

    print("BACKEND AUDIT FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main_audit())
