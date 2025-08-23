from dataclasses import dataclass, field
from yarl import URL


@dataclass
class RequestOptions:
    """
    Option set for SessionManager.get() and post()
    Accepts URL, parameters and flag to sync cookies from active session
    """

    url: URL
    params: dict[str, str] = field(default_factory=dict[str, str])
    sync_cookies: bool = field(default=False)

    def __str__(self) -> str:
        s = str(self.url)
        if self.params:
            s += "?" + "&".join(f"{k}={v}" for k, v in self.params.items())
        return s


@dataclass
class RequestStats:
    """
    Base class for storing request stats:
    - Status
    - Completion time
    - Content size
    """

    status: int
    time: float = field(default=0.0)
    size: int = field(default=0)


@dataclass
class PageRequestStats(RequestStats):
    f"""
    Stores base and rating page specific request stats:
    - Status
    - Completion time
    - Content size
    - Rating page number
    - Resulting show count
    """

    page: int = field(default=0)
    shows: int = field(default=0)

    # def __init__(self, base_stats: RequestStats, page: int, shows: int = 0) -> None:
    #     self.status = base_stats.status
    #     self.time = base_stats.time
    #     self.size = base_stats.size
    #     self.page = page
    #     self.shows = shows


# WIP
# @dataclass
# class ShowRequestStats(RequestStats):

#     show_id: int
