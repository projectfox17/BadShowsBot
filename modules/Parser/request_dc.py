"""
Contains dataclasses:
- Request options for SessionManager
- Request results for Parser
"""

from dataclasses import dataclass, field
from yarl import URL

from modules.ShowData import ShowIDs


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
        s = self.url
        if self.params:
            s += "?" + "=".join(f"{k}={v}" for k, v in self.params.items())
        return s


@dataclass
class RequestResult:
    """
    Contains ShowID class with request results and stats for network analytics
    """

    result: ShowIDs | None
    page: int
    status: int = field(default=0)
    time: float = field(default=0.0)
    size: int = field(default=0)
    n_matches: int = field(default=0)
    n_shows: int = field(default=0)

    def stats_as_csv(self, sep: str = "; ") -> str:
        """
        Returns request stats separated with specified string in following order:
        Page, status, time, text length, number of matched links, resulting number of shows
        """

        s = "; ".join(
            str(attr)
            for attr in (
                self.page,
                self.status,
                self.time,
                self.size,
                self.n_matches,
                self.n_shows,
            )
        )
        return s
