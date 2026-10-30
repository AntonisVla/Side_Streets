import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "learning.db"
DATABASE_PATH.parent.mkdir(parents=True,exist_ok=True)

connection = sqlite3.connect(DATABASE_PATH)

try:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        neighborhood TEXT NOT NULL,
        address TEXT NOT NULL,
        description TEXT NOT NULL,
        tip TEXT NOT NULL 
        )
        """
    )

    connection.commit()
    print(f"Database ready: {DATABASE_PATH}")

finally:
    connection.close()
