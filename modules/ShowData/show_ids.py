from dataclasses import dataclass, field


@dataclass
class ShowIDs:
    films: set[int] = field(default_factory=set)
    series: set[int] = field(default_factory=set)
    
    @property
    def total(self) -> int:
        return len(self.films) + len(self.series)
