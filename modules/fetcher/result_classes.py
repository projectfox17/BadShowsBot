from typing import Optional
from dataclasses import dataclass, field

from modules.fetcher import RequestStats
from modules.show_classes import ShowInfo, ShowIDContainer


@dataclass
class RatingPageParseStats:
    page: int
    show_count: int = field(default=0)
    time: float = field(default=0)


@dataclass
class RatingPageFetchResult:
    request_stats: RequestStats
    parse_stats: RatingPageParseStats
    show_ids: Optional[ShowIDContainer] = field(default=None)


@dataclass
class BulkRatingPageFetchResult:
    results_by_page: dict[int, Optional[RatingPageFetchResult]] = field(
        default_factory=dict
    )
    total_time: float = field(default=0.0)

    def join_id_containers(self) -> ShowIDContainer:
        joined = ShowIDContainer()
        for res in self.results_by_page.values():
            if res and res.show_ids:
                joined.merge(res.show_ids)
        return joined


@dataclass
class ShowInfoFetchResult:
    show_id: int
    request_stats: RequestStats
    show_info: Optional[ShowInfo] = field(default=None)
    parse_time: float = field(default=0)


@dataclass
class BulkShowInfoFetchResult:
    results_by_id: dict[int, Optional[ShowInfoFetchResult]] = field(
        default_factory=dict
    )
    total_time: float = field(default=0.0)

    def show_info_list(self) -> list[ShowInfo]:
        lst: list[ShowInfo] = [
            res.show_info
            for res in self.results_by_id.values()
            if res and res.show_info
        ]
        return lst
