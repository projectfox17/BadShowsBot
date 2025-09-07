from typing import Optional
from enum import Enum
from dataclasses import dataclass, field


class ShowType(Enum):
    FILM = "film"
    SERIES = "series"


@dataclass
class ShowInfo:
    show_id: int
    show_type: ShowType
    rating: float
    description: str


@dataclass
class ShowIDContainer:
    films: set[int] = field(default_factory=set)
    series: set[int] = field(default_factory=set)

    def merge(self, other: "ShowIDContainer"):
        self.merge_fields(films=other.films, series=other.series)

    def merge_fields(
        self, films: Optional[set[int]] = None, series: Optional[set[int]] = None
    ):
        if films:
            self.films.update(films)
        if series:
            self.films.update(series)

    def total_count(self) -> int:
        return len(self.films) + len(self.series)
