from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer
from enum import Enum
from typing import Set, Optional, List


BAD_SYMBOLS = {"\n": " ", "\xa0": " "}


class ShowIDContainer(BaseModel):
    films: Set[int] = Field(default_factory=set)
    series: Set[int] = Field(default_factory=set)

    def merge(self, other: "ShowIDContainer"):
        self.merge_fields(films=other.films, series=other.series)

    def merge_fields(
        self, films: Optional[Set[int]] = None, series: Optional[Set[int]] = None
    ):
        self.films.update(films or set())
        self.series.update(films or set())

    @property
    def total_count(self) -> int:
        return len(self.films) + len(self.series)


class ShowType(Enum):
    FILM = "film"
    SERIES = "series"


class ShowInfo(BaseModel):
    title: str
    rating: float
    rating_count: int
    description: str
    genres: List[str]

    model_config = ConfigDict(from_attributes=True)

    # @field_validator("title", mode="before")
    # def validate_title(cls, title: str):
    #     # replace bad symbols
    #     return title

    @field_validator("description", mode="before")
    def validate_description(cls, description: str):
        for s in BAD_SYMBOLS:
            if s in description:
                description = description.replace(s, BAD_SYMBOLS[s])
        return description


class Show(BaseModel):
    id: int
    type: ShowType
    info: Optional[ShowInfo] = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    @field_validator("type", mode="before")
    def validate_type(cls, v: ShowType | str):
        if isinstance(v, ShowType):
            return v
        if isinstance(v, str):
            v = v.upper()
            if v not in ("FILM", "SERIES"):
                raise ValueError(f"Invalid show type key: {v}, expected FILM or SERIES")
            return ShowType[v]

    @field_serializer
    def serialize_type(self, v: ShowType):
        return v.value
