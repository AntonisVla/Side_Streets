import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

APP_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIRECTORY.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "side_streets.db"

SELECT_PLACE = """
    SELECT
        places.id,
        places.name,
        places.category,
        places.neighborhood,
        places.address,
        places.description,
        places.tip,
        shortlist.place_id IS NOT NULL AS shortlisted
    FROM places
    LEFT JOIN shortlist ON shortlist.place_id = places.id
"""
EDITABLE = ("name", "category", "neighborhood", "address", "description", "tip")


@contextmanager
def connect():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def to_place(row):
    place = dict(row)
    place["shortlisted"] = bool(place["shortlisted"])
    return place


def fetch_place(connection, place_id: int):
    row = connection.execute(
        SELECT_PLACE + " WHERE places.id = ?",
        (place_id,),
    ).fetchone()

    return None if row is None else to_place(row)


def initialize():
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
    sql = SELECT_PLACE
    conditions = []
    parameters = []

    if category is not None:
        conditions.append("places.category = ?")
        parameters.append(category)

    search_text = q.strip()

    if search_text:
        conditions.append(
            """
            instr(
                lower(places.name || ' ' || places.neighborhood || ' ' || places.description),
                lower(?)
            ) > 0
            """
        )
        parameters.append(search_text)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY places.id"

    with connect() as connection:
        rows = connection.execute(sql, parameters).fetchall()
        return [to_place(row) for row in rows]


def get_place(place_id: int):
    with connect() as connection:
        return fetch_place(connection, place_id)


def create_place(data: dict):
    with connect() as connection:
        cursor = connection.execute(
            f"""
            INSERT INTO places ({", ".join(EDITABLE)})
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [data[field] for field in EDITABLE],
        )

        return fetch_place(connection, cursor.lastrowid)


def update_place(place_id: int, data: dict):
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

        return fetch_place(connection, place_id)


def delete_place(place_id: int):
    with connect() as connection:
        cursor = connection.execute(
            "DELETE FROM places WHERE id = ?",
            (place_id,),
        )

        return cursor.rowcount > 0


def list_shortlist():
    with connect() as connection:
        rows = connection.execute(
            SELECT_PLACE
            + " WHERE shortlist.place_id IS NOT NULL ORDER BY places.id"
        ).fetchall()

        return [to_place(row) for row in rows]


def set_shortlisted(place_id: int, shortlisted: bool):
    with connect() as connection:
        place = fetch_place(connection, place_id)

        if place is None:
            return None

        if shortlisted and not place["shortlisted"]:
            connection.execute(
                "INSERT INTO shortlist (place_id) VALUES (?)",
                (place_id,),
            )

        if not shortlisted:
            connection.execute(
                "DELETE FROM shortlist WHERE place_id = ?",
                (place_id,),
            )

        return fetch_place(connection, place_id)


if __name__ == "__main__":
    initialize()
    print(f"DATABASE initialized: {DATABASE_PATH}")
