from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response

from . import db
from .models import PlaceInput


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Create tables and seed sample data before serving requests.
    db.initialize()
    yield


app = FastAPI(title="Side Streets", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/places")
def list_places(q: str = "", category: str | None = None):
    return db.list_places(q=q, category=category)


@app.get("/api/places/{place_id}")
def get_place(place_id: int):
    place = db.get_place(place_id)

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return place


@app.post("/api/places", status_code=201)
def create_place(place: PlaceInput):
    # The database layer receives plain data, not Pydantic objects.
    return db.create_place(place.model_dump())


@app.put("/api/places/{place_id}")
def update_place(place_id: int, data: PlaceInput):
    place = db.update_place(place_id, data.model_dump())

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return place


@app.delete("/api/places/{place_id}", status_code=204)
def delete_place(place_id: int):
    if not db.delete_place(place_id):
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return Response(status_code=204)
