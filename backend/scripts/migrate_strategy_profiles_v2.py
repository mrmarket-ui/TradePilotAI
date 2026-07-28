from __future__ import annotations

from sqlalchemy import inspect, text

from database.database import engine


TABLE_NAME = "strategy_profiles"


POSTGRES_COLUMNS = {
    "strategy_type":
        "VARCHAR(40) NOT NULL DEFAULT 'Day Trading'",

    "version":
        "VARCHAR(20) NOT NULL DEFAULT '1.0'",

    "icon":
        "VARCHAR(50)",

    "color":
        "VARCHAR(20) DEFAULT '#2563EB'",

    "is_favorite":
        "BOOLEAN NOT NULL DEFAULT FALSE",

    "ai_notes":
        "TEXT",

    "allowed_symbols":
        "JSON NOT NULL DEFAULT '[]'::json",

    "blocked_symbols":
        "JSON NOT NULL DEFAULT '[]'::json",

    "preferred_direction":
        "VARCHAR(10) NOT NULL DEFAULT 'BOTH'",

    "allowed_weekdays":
        "JSON NOT NULL DEFAULT '[]'::json",

    "trading_start_time":
        "VARCHAR(10)",

    "trading_end_time":
        "VARCHAR(10)",

    "timezone":
        "VARCHAR(60) DEFAULT 'UTC'",

    "pre_trade_checklist":
        "JSON NOT NULL DEFAULT '[]'::json",

    "post_trade_checklist":
        "JSON NOT NULL DEFAULT '[]'::json",

    "min_risk_reward":
        "DOUBLE PRECISION NOT NULL DEFAULT 2.0",

    "max_open_positions":
        "INTEGER NOT NULL DEFAULT 1",

    "max_lot_size":
        "DOUBLE PRECISION",

    "move_to_breakeven_at_rr":
        "DOUBLE PRECISION DEFAULT 1.0",

    "partial_take_profit_percent":
        "DOUBLE PRECISION DEFAULT 50.0",

    "avoid_high_impact_news":
        "BOOLEAN NOT NULL DEFAULT TRUE",

    "news_minutes_before":
        "INTEGER NOT NULL DEFAULT 30",

    "news_minutes_after":
        "INTEGER NOT NULL DEFAULT 30",

    "ai_setup_scoring_enabled":
        "BOOLEAN NOT NULL DEFAULT TRUE",

    "ai_coach_enabled":
        "BOOLEAN NOT NULL DEFAULT TRUE",

    "auto_chart_analysis":
        "BOOLEAN NOT NULL DEFAULT FALSE",

    "auto_journal_enabled":
        "BOOLEAN NOT NULL DEFAULT TRUE",

    "weekly_ai_review_enabled":
        "BOOLEAN NOT NULL DEFAULT TRUE",

    "monthly_ai_review_enabled":
        "BOOLEAN NOT NULL DEFAULT TRUE",

    "automation_enabled":
        "BOOLEAN NOT NULL DEFAULT FALSE",

    "is_archived":
        "BOOLEAN NOT NULL DEFAULT FALSE",
}


def main() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError(
            "This migration is intended for PostgreSQL. "
            f"Detected: {engine.dialect.name}"
        )

    inspector = inspect(engine)

    if TABLE_NAME not in inspector.get_table_names():
        raise RuntimeError(
            f"Table '{TABLE_NAME}' does not exist."
        )

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(TABLE_NAME)
    }

    added: list[str] = []
    skipped: list[str] = []

    with engine.begin() as connection:
        for name, definition in POSTGRES_COLUMNS.items():
            if name in existing_columns:
                skipped.append(name)
                continue

            connection.execute(
                text(
                    f'ALTER TABLE "{TABLE_NAME}" '
                    f'ADD COLUMN IF NOT EXISTS "{name}" '
                    f"{definition}"
                )
            )

            added.append(name)

    print(
        f"Migration complete. Added {len(added)} columns."
    )

    for name in added:
        print(f"  ADDED: {name}")

    for name in skipped:
        print(f"  EXISTS: {name}")


if __name__ == "__main__":
    main()
