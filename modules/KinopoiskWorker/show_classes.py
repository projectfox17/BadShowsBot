from enum import Enum
from dataclasses import dataclass, field


@dataclass
class ShowIDs:

    films: set[int] = field(default_factory=set)
    series: set[int] = field(default_factory=set)

    @property
    def total(self) -> int:
        return len(self.films) + len(self.series)


class ShowType(Enum):

    FILM = "film"
    SERIES = "series"


@dataclass
class ShowInfo:

    show_id: int
    show_type: ShowType
    title: str
    rating: float = field(default=0.0)
    description: str = field(default="")
