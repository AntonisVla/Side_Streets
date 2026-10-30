import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "learning.db"

if not DATABASE_PATH.exists():
    raise SystemExit("Run scripts/create_db.py first")

connection = sqlite3.connect(DATABASE_PATH)
connection.row_factory = sqlite3.Row

try:

    cursor = connection.execute(
        """
        SELECT id, name, category, neighborhood, address, description, tip
        FROM places
        ORDER BY id
        """
    )

    places = cursor.fetchall()

    print(f"Found {len(places)} places")

    for place in places:
        print(
          f"{place['id']} |"
          f"{place['name']} |"
          f"{place['category']} |"
          f"{place['neighborhood']} |"
          f"{place['address']} |"
          f"{place['description']} |"
          f"{place['tip']}"
        )

finally:
    connection.close()
