from fastapi import FastAPI, HTTPException

from .models import PlaceInput

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


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/places")
def list_places(q: str = "", category: str | None = None):
    search_text = q.strip().casefold()
    matching_places = []

    for place in PLACES:
        if category is not None and place["category"] != category:
            continue

        searchable_text = " ".join(
            [
                place["name"],
                place["neighborhood"],
                place["description"],
            ]
        ).casefold()

        if search_text and search_text not in searchable_text:
            continue

        matching_places.append(place)

    return matching_places


@app.get("/api/places/{place_id}")
def get_place(place_id: int):
    for place in PLACES:
        if place["id"] == place_id:
            return place

    raise HTTPException(
        status_code=404,
        detail="This place does not exist.",
    )


@app.post("/api/places", status_code=201)
def create_place(place: PlaceInput):
    next_id = max(
        (place["id"] for place in PLACES),
        default=0,
    ) + 1

    new_place = place.model_dump()

    new_place["id"] = next_id
    new_place["shortlisted"] = False

    PLACES.append(new_place)

    return new_place


@app.put("/api/places/{place_id}")
def update_place(place_id: int, data: PlaceInput):
    for index, place in enumerate(PLACES):
        if place["id"] == place_id:
            updated_place = data.model_dump()

            updated_place["id"] = place_id
            updated_place["shortlisted"] = place["shortlisted"]

            PLACES[index] = updated_place

            return updated_place

    raise HTTPException(
        status_code=404,
        detail="This place does not exist.",
    )


@app.delete("/api/places/{place_id}", status_code=204)
def delete_place(place_id: int):
    for index, place in enumerate(PLACES):
        if place["id"] == place_id:
            PLACES.pop(index)
            return

    raise HTTPException(
        status_code=404,
        detail="This place does not exist.",
    )
