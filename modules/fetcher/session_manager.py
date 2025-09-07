import aiohttp
from typing import Optional

from modules.fetcher import RequestOptions, RequestStats, RequestResult
from modules.timer import AsyncTimer


class SessionManager:
    def __init__(
        self,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
    ):
        self._session = ...
