from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Set, Optional, Literal


BAD_SYMBOLS = []


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


class ShowInfo(BaseModel):
    show_id: int
    title: str
    show_type: Literal["FILM", "SERIES"]
    rating: float
    description: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("title", mode="before")
    def validate_title(cls, title: str):
        # replace bad symbols
        return title

    @field_validator("description", mode="before")
    def validate_description(cls, description: str):
        # replace bad symbols
        return description
