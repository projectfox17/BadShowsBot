from typing import Optional
from enum import Enum
from dataclasses import dataclass, field
from yarl import URL


class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"


@dataclass(frozen=True)
class RequestOptions:
    url: URL
    method: RequestMethod = field(default=RequestMethod.GET)
    params: dict[str, str] = field(default_factory=dict)
    sync_cookies: bool = field(default=False)

    def final_url(self) -> URL:
        return self.url.update_query(self.params)

    def __repr__(self) -> str:
        return (
            f"RequestOptions(url={self.final_url()}, sync_cookies={self.sync_cookies})"
        )


@dataclass
class RequestStats:
    options: RequestOptions
    status: int  # Consider 0 for failed for non-networking reason
    time: float = field(default=0.0)
    size: int = field(default=0)


@dataclass
class RequestResult:
    stats: RequestStats
    content: str | bytes | None = field(default=None)
