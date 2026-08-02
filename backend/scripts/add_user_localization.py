import main

from sqlalchemy import text
from database.database import engine

with engine.begin() as connection:
    connection.execute(
        text(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS
            preferred_language VARCHAR(10)
            NOT NULL DEFAULT 'en'
            """
        )
    )

    connection.execute(
        text(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS
            preferred_currency VARCHAR(10)
            NOT NULL DEFAULT 'USD'
            """
        )
    )

print("User localization columns added successfully.")
