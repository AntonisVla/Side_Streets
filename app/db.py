import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

APP_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIRECTORY.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "side_streets.db"

COLUMNS = "id, name, category, neighborhood, address, description, tip, shortlisted"
EDITABLE = ("name", "category", "neighborhood", "address", "description", "tip")


@contextmanager
def connect():
    """Open a connection; commit on success, roll back on error, always close."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def to_place(row):
    place = dict(row)
    place["shortlisted"] = bool(place["shortlisted"])
    return place


def initialize():
    """Create missing tables and insert the sample places only once."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = (APP_DIRECTORY / "schema.sql").read_text(encoding="utf-8")

    with connect() as connection:
        connection.executescript(schema)
        connection.execute("BEGIN IMMEDIATE")

        seeded = connection.execute(
            "SELECT value FROM app_metadata WHERE key = ?",
            ("seeded",),
        ).fetchone()

        if seeded is not None:
            return

        seed_text = (APP_DIRECTORY / "seed.json").read_text(encoding="utf-8")

        for place in json.loads(seed_text):
            connection.execute(
                f"""
                INSERT INTO places ({", ".join(EDITABLE)})
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [place[field] for field in EDITABLE],
            )

        connection.execute(
            "INSERT INTO app_metadata (key, value) VALUES (?, ?)",
            ("seeded", "1"),
        )


def list_places(q: str = "", category: str | None = None):
    """Return places matching the optional text and category filters."""
    sql = f"SELECT {COLUMNS} FROM places"
    conditions = []
    parameters = []

    if category is not None:
        conditions.append("category = ?")
        parameters.append(category)

    search_text = q.strip()

    if search_text:
        conditions.append(
            """
            instr(
                lower(name || ' ' || neighborhood || ' ' || description),
                lower(?)
            ) > 0
            """
        )
        parameters.append(search_text)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY id"

    with connect() as connection:
        rows = connection.execute(sql, parameters).fetchall()
        return [to_place(row) for row in rows]


def get_place(place_id: int):
    """Return a place dictionary, or None if the ID does not exist."""
    with connect() as connection:
        row = connection.execute(
            f"SELECT {COLUMNS} FROM places WHERE id = ?",
            (place_id,),
        ).fetchone()

        return None if row is None else to_place(row)


def create_place(data: dict):
    """Insert a place and return its stored content."""
    with connect() as connection:
        cursor = connection.execute(
            f"""
            INSERT INTO places ({", ".join(EDITABLE)})
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [data[field] for field in EDITABLE],
        )

        row = connection.execute(
            f"SELECT {COLUMNS} FROM places WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return to_place(row)


def update_place(place_id: int, data: dict):
    """Replace a place's editable fields, or return None if it is missing."""
    with connect() as connection:
        cursor = connection.execute(
            f"""
            UPDATE places
            SET {", ".join(f"{field} = ?" for field in EDITABLE)}
            WHERE id = ?
            """,
            [*(data[field] for field in EDITABLE), place_id],
        )

        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            f"SELECT {COLUMNS} FROM places WHERE id = ?",
            (place_id,),
        ).fetchone()

        return to_place(row)


def delete_place(place_id: int):
    """Return True if a place was deleted, or False if it was missing."""
    with connect() as connection:
        cursor = connection.execute(
            "DELETE FROM places WHERE id = ?",
            (place_id,),
        )

        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize()
    print(f"DATABASE initialized: {DATABASE_PATH}")