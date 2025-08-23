import aiohttp
from typing import Optional

from modules.KinopoiskWorker import RequestOptions, RequestStats
from modules.Timer import AsyncTimer
from modules.Logger import Logger


logger = Logger("SessionManager")


class SessionManager:

    def __init__(
        self,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
    ) -> None:

        self._session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())
        self._headers = headers or {}
        self.update_headers(self._headers)
        self._cookies = cookies or {}
        self.update_cookies(self._cookies)
        
        logger.debug("Session initialized")

    async def close_session(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        
        logger.debug("Session closed")

    # Async context manager stuff

    async def __aenter__(self, *args):
        return self

    async def __aexit__(self, *args) -> None:
        await self.close_session()

    # Headers and cookies loading

    def update_headers(
        self, headers: dict[str, str], overwrite_conflicts: bool = True
    ) -> None:

        logger.debug("Updating session headers")

        counter: int = 0
        for name, value in headers.items():
            if not overwrite_conflicts and name in self._headers:
                continue
            self._headers[name] = value
            counter += 1

        self._session.headers.update(self._headers)
        logger.debug(f"{counter} headers updated, total {len(self._headers)}")

    def update_cookies(
        self, cookies: dict[str, str], overwrite_conflicts: bool = True
    ) -> None:

        logger.debug("Updating session cookies")

        counter: int = 0
        for name, value in cookies.items():
            if not overwrite_conflicts and name in self._cookies:
                continue
            self._cookies[name] = value
            counter += 1

        self._session.cookie_jar.update_cookies(self._cookies)
        logger.debug(f"{counter} cookies updated, total {len(self._cookies)}")

    # Requests

    async def get(
        self, options: RequestOptions, attempts: int = 3
    ) -> tuple[str, RequestStats]:

        opt_str = str(options)

        for a in range(attempts):
            try:
                logger.debug(f"Requesting GET {opt_str} attempt {a + 1}")
                async with AsyncTimer() as timer:

                    async with self._session.get(
                        url=options.url, params=options.params
                    ) as resp:

                        if resp.status != 200:
                            logger.warning(
                                f"Requesting GET {opt_str} status {resp.status}, retrying"
                            )
                            continue

                        content: str = await resp.text()
                        req_stats = RequestStats(
                            resp.status, timer.elapsed, len(content)
                        )

                        if options.sync_cookies:
                            session_cookies: dict[str, str] = {
                                str(n): str(v.value) for n, v in resp.cookies.items()
                            }
                            self.update_cookies(session_cookies)

                        logger.debug(f"Requesting GET {opt_str} done")
                        return content, req_stats

            except aiohttp.ClientError as cle:
                logger.warning(f"ClientError on requesting GET {opt_str}:\n{cle}")

            except Exception as e:
                logger.warning(f"Exception on requesting GET {opt_str}:\n{e}")

        else:
            logger.error(f"Requesting GET {opt_str} failed, {attempts} unsuccessful")
            return None, None
