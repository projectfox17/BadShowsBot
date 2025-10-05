from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    model_serializer,
    field_validator,
    field_serializer,
)
from enum import Enum
from typing import List, Dict, Any


class ShowType(Enum):
    FILM = "film"
    SERIES = "series"


class ShowIdentifier(BaseModel):
    id: int
    type: ShowType

    @field_validator("type", mode="before")
    def validate_type(cls, v: str | ShowType):
        if isinstance(v, str):
            if v not in ("film", "series"):
                raise ValueError(f"Invalid show type {v}")
            v = ShowType(v)
        return v

    @field_serializer("type")
    def serialize_type(self, type: ShowType, _info):
        return type.value

    def __str__(self):
        return f"{self.type.value}/{self.id}"


class ShowDetails(BaseModel):
    title: str
    rating: float
    rating_count: int
    description: str
    genres: List[str]


class ShowModel(BaseModel):
    identifier: ShowIdentifier
    details: ShowDetails

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: Dict[str, Any]):
        if "identifier" in data and "details" in data:
            return data

        identifier = {"id": data["id"], "type": data["type"]}
        details = {
            "title": data["title"],
            "rating": data["rating"],
            "rating_count": data["rating_count"],
            "description": data["description"],
            "genres": data["genres"],
        }
        return {"identifier": identifier, "details": details}

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return {
            "id": self.identifier.id,
            "type": self.identifier.type.value,
            "title": self.details.title,
            "rating": self.details.rating,
            "rating_count": self.details.rating_count,
            "description": self.details.description,
            "genres": self.details.genres,
        }
