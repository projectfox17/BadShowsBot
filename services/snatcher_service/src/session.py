from aiohttp import ClientSession, CookieJar
from time import sleep
from random import randint
from yarl import URL
from typing import Optional, Literal

from common.logger import Logger
from common.timer import Timer
from src.models import SessionConfig, RequestResult


logger = Logger("SessionManager")


class SessionManager:
    """
    Обертка для aiohttp.ClientSession: запросы обращаются
    к единственной запущенной при инициализации сессии.\n
    Cookies и заголовки хранятся в SessionConfig,
    могут быть синхронизированы с актуальными в сессии и
    экспортированы извне через `SessionManager.config`.
    """

    def __init__(self, config: Optional[SessionConfig] = None):
        self._session = ClientSession(cookie_jar=CookieJar())
        self.config = config or SessionConfig()
        self._session.headers.update(self.config.headers)
        self._session.cookie_jar.update_cookies(self.config.cookies)

        logger.debug("Session initialized")

    async def close_session(self) -> None:
        if not self._session.closed:
            await self._session.close()

    async def __aenter__(self, *args) -> "SessionManager":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close_session()

    def update_config(
        self,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        overwrite: bool = True,
        keep_old: bool = True,
    ):
        if headers:
            if not keep_old:
                self.headers.clear()
            logger.debug(f"Updating config headers")
            upd_count = 0
            for k, v in headers.items():
                if not overwrite and k in self.config.headers:
                    continue
                self.config.headers[str(k)] = str(v)
                upd_count += 1
            logger.debug(
                f"Updated {upd_count} headers, total {len(self.config.headers)}"
            )
            self._session.headers.update(self.config.headers)

        if cookies:
            if not keep_old:
                self.cookies.clear()
            logger.debug(f"Updating config cookies")
            upd_count = 0
            for k, v in cookies.items():
                if not overwrite and k in self.config.cookies:
                    continue
                self.config.cookies[str(k)] = str(v)
                upd_count += 1
            logger.debug(
                f"Updated {upd_count} cookies, total {len(self.config.cookies)}"
            )
            self._session.cookie_jar.update_cookies(self.config.cookies)

    async def request(
        self,
        url: str | URL,
        method: Literal["GET", "POST"],
        params: Optional[dict[str, any]] = None,
        sync_config: bool = False,
        attempts: int = 3,
    ) -> RequestResult:
        params = params or {}
        url = str(URL(url).with_query(params))
        if not url.startswith("http"):
            url = "http://" + url

        time = 0.0
        status = 0
        for attempt in range(1, attempts + 1):
            if attempt > 1:
                sleep(randint(attempt, attempt * 2))

            timer = Timer()
            try:
                logger.debug(
                    f"{method} {url}"
                    + (f", attempt {attempt}" if attempt > 1 else "")
                    + "..."
                )
                if method == "GET":
                    response = await self._session.get(url)
                elif method == "POST":
                    response = await self._session.post(url)
                time = timer.elapsed
                status = response.status

                if status != 200:
                    logger.warning(f"Status {status} on {method} {url}")
                    continue

                content: str = await response.text()

                if sync_config:
                    logger.debug(f"Syncing cookies from {url}")
                    new_cookies = {n: v.value for n, v in response.cookies.items()}
                    self.update_config(cookies=new_cookies)

                logger.debug(f"Done {method} {url} in {time:.3f}s")
                return RequestResult(content=content, url=url, time=time, status=status)

            except Exception as e:
                logger.warning(f"Error on {method} {url}: {e}")

        logger.error(f"Failed {method} {url}")
        return RequestResult(content=None, url=url, time=time, status=status)
