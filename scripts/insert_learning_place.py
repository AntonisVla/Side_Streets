import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "learning.db"

if not DATABASE_PATH.exists():
    raise SystemExit("Run scripts/create_learning_db.py first")

connection = sqlite3.connect(DATABASE_PATH)

try:

    values = (
        "The Sunday Room",
        "Coffee & bites",
        "Old Town",
        "12 Lantern Lane",
        "A sunny corner cafe serving slow-brewed coffee and fresh "
        "pastries, with mismatched armchairs and plenty of window seats.",
        "Arrive before nine for the best seats by the window.",
    )

    cursor = connection.execute(
        """
        INSERT INTO places(
        name,
        category,
        neighborhood,
        address,
        description,
        tip
        )
        VALUES(?, ?, ?, ?, ?, ?)
        """,
        values,
    )

    connection.commit()

    print(f"Created place with ID {cursor.lastrowid} ")

except sqlite3.Error:
    connection.rollback()
    raise

finally:
    connection.close()
