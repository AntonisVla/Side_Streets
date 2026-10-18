from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal[
    "Coffee & bites",
    "Art & culture",
    "Outdoors",
    "Little shops",
]


class PlaceInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
    name: str = Field(min_length=2, max_length=80)
    category: Category
    neighborhood: str = Field(min_length=2, max_length=60)
    address: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=20, max_length=1000)
    tip: str = Field(min_length=5, max_length=400)