"""
One-time cleanup: remove trades created by the OLD per-deal MT5 importer.

Old rows are imported trades whose ticket does not start with "mt5:". The new
importer builds one trade per closed position and prefixes every ticket with
"mt5:<server>:<account>:", so the two kinds never mix.

Default is a DRY RUN: it prints counts only and writes a backup CSV.
Pass --delete to actually remove the rows (the backup is written first).

Run from the backend folder:
    python scripts/cleanup_legacy_imports.py
    python scripts/cleanup_legacy_imports.py --delete
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from sqlalchemy import or_  # noqa: E402

from database.database import get_db  # noqa: E402
from models.trade import Trade  # noqa: E402

COLUMNS = [
    "id", "user_id", "broker", "ticket", "pair", "direction", "entry",
    "exit_price", "lot_size", "profit", "commission", "swap",
    "opened_at", "closed_at", "imported",
]


def legacy_rows(db):
    return (
        db.query(Trade)
        .filter(
            Trade.imported.is_(True),
            or_(
                Trade.ticket.is_(None),
                ~Trade.ticket.like("mt5:%"),
            ),
        )
        .order_by(Trade.id)
        .all()
    )


def write_backup(rows, folder: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = folder / f"legacy_imported_trades.before-cleanup-{stamp}.csv"

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([getattr(row, name, "") for name in COLUMNS])

    return path


def run(db, delete: bool, folder: Path) -> dict:
    rows = legacy_rows(db)

    result = {
        "found": len(rows),
        "deleted": 0,
        "backup": None,
        "by_user_and_broker": dict(
            Counter((row.user_id, row.broker) for row in rows)
        ),
    }

    if not rows:
        return result

    result["backup"] = write_backup(rows, folder)

    if delete:
        for row in rows:
            db.delete(row)
        db.commit()
        result["deleted"] = len(rows)

    return result


def main() -> None:
    delete = "--delete" in sys.argv
    db = next(get_db())

    try:
        print(f"Database engine: {db.get_bind().dialect.name}")
        result = run(db, delete, BACKEND)
    finally:
        db.close()

    print(f"Old-format imported trades found: {result['found']}")

    for (user_id, broker), count in result["by_user_and_broker"].items():
        print(f"  user {user_id}, broker {broker!r}: {count}")

    if result["backup"]:
        print(f"Backup written to: {result['backup']}")

    if not result["found"]:
        print("Nothing to clean up.")
    elif delete:
        print(f"DELETED {result['deleted']} rows.")
    else:
        print("Dry run only: nothing was deleted. Re-run with --delete to remove them.")


if __name__ == "__main__":
    main()