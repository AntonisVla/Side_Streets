from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response

from . import db
from .models import Category, Place, PlaceInput, ShortlistInput

router = APIRouter(prefix="/api", tags=["Side Streets"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/places", response_model=list[Place])
def list_places(
    q: Annotated[
        str,
        Query(
            max_length=100,
            description="Search the name, neighborhood, or description",
        ),
    ] = "",
    category: Category | None = None,
):
    return db.list_places(q=q, category=category)


@router.get("/places/{place_id}", response_model=Place)
def get_place(place_id: int):
    place = db.get_place(place_id)

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return place


@router.post("/places", status_code=201, response_model=Place)
def create_place(data: PlaceInput):
    return db.create_place(data.model_dump())


@router.put("/places/{place_id}", response_model=Place)
def update_place(place_id: int, data: PlaceInput):
    place = db.update_place(place_id, data.model_dump())

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return place


@router.delete("/places/{place_id}", status_code=204)
def delete_place(place_id: int):
    if not db.delete_place(place_id):
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return Response(status_code=204)


@router.get("/shortlist", response_model=list[Place])
def list_shortlist():
    return db.list_shortlist()


@router.put("/places/{place_id}/shortlist", response_model=Place)
def set_shortlist(place_id: int, data: ShortlistInput):
    place = db.set_shortlisted(place_id, data.shortlisted)

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="This place does not exist.",
        )

    return place