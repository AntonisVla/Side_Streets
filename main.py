from fastapi import FastAPI, HTTPException

app = FastAPI(title="Side Streets")

PLACES = [
    {
        "id": 1,
        "name": "The Sunday Room",
        "category": "Coffee & bites",
        "neighborhood": "Old Town",
        "address": "12 Lantern Lane",
        "description": (
            "A sunny corner cafe serving slow-brewed coffee and fresh "
            "pastries, with mismatched armchairs and plenty of window seats."
        ),
        "tip": "Arrive before nine for the best seats by the window.",
        "shortlisted": False,
    },
    {
        "id": 2,
        "name": "Saltwater Steps",
        "category": "Outdoors",
        "neighborhood": "Harbour",
        "address": "Pier Road, east end",
        "description": (
            "A series of wide stone steps leading down to the water, "
            "popular for sunrise walks and a quiet swim."
        ),
        "tip": "Wear shoes with grip because the lower steps stay slippery.",
        "shortlisted": False,
    },
    {
        "id": 3,
        "name": "Ink & Paper",
        "category": "Little shops",
        "neighborhood": "Old Town",
        "address": "7 Printer's Alley",
        "description": (
            "A tiny independent bookshop and stationer packed with "
            "notebooks, pens, and carefully chosen second-hand paperbacks."
        ),
        "tip": "Ask the owner for recommendations from the back shelf.",
        "shortlisted": False,
    },
]

CATEGORIES = ["Coffee & bites", "Art & culture", "Outdoors", "Little shops"]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/places")
def list_places(q: str = "", category: str | None = None):
    """Return places, optionally filtered by search text and/or category."""
    search_text = q.strip().casefold()
    matching = []

    for place in PLACES:
        if category is not None and place["category"] != category:
            continue

        searchable = " ".join(
            [place["name"], place["neighborhood"], place["description"]]
        ).casefold()

        if search_text and search_text not in searchable:
            continue

        matching.append(place)

    return matching  


@app.get("/api/places/{place_id}")
def get_place(place_id: int):
    for place in PLACES:
        if place["id"] == place_id:
            return place
    raise HTTPException(status_code=404, detail="This place does not exist.")