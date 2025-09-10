from aiohttp import ClientSession, CookieJar, ClientError
from time import sleep
from random import randint
from typing import Optional

from modules.fetcher import RequestOptions, RequestStats, RequestResult
from modules.async_timer import AsyncTimer
from modules.logger import Logger


logger = Logger("Session Manager")


class SessionManager:
    def __init__(
        self,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
    ):
        self._session = ClientSession(cookie_jar=CookieJar())
        logger.debug("Session initialized")

        self._headers = headers or {}
        self._cookies = cookies or {}
        self.update_session(headers=self._headers, cookies=self._cookies)

    async def close_session(self):
        if self._session and not self._session.closed:
            await self._session.close()

        logger.debug("Session closed")

    async def __aenter__(self, *args):
        return self

    async def __aexit__(self, *args):
        await self.close_session()

    def update_session(
        self,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        overwrite: bool = True,
        keep_old: bool = True,
    ):
        if headers:
            logger.debug(f"Updating session headers")
            if not keep_old:
                self._headers.clear()

            upd_count = 0
            for k, v in headers.items():
                if not overwrite and k in self._headers:
                    continue
                self._headers[str(k)] = str(v)
                upd_count += 1
            self._session.headers.update(self._headers)
            logger.debug(f"Updated {upd_count} headers, total {len(self._headers)}")

        if cookies:
            logger.debug(f"Updating session cookies")
            if not keep_old:
                self._cookies.clear()

            upd_count = 0
            for k, v in cookies.items():
                if not overwrite and k in self._cookies:
                    continue
                self._cookies[str(k)] = str(v)
                upd_count += 1
            self._session.cookie_jar.update_cookies(self._cookies)
            logger.debug(f"Updated {upd_count} cookies, total {len(self._cookies)}")

    async def request(
        self, options: RequestOptions, attempts: int = 3
    ) -> RequestResult:
        r_status = r_time = None
        for attempt in range(1, attempts + 1):
            if attempt > 1:
                sleep(2 * attempt)
            async with AsyncTimer() as timer:
                try:
                    logger.debug(
                        f"Requesting {options.method} {options.final_url} attempt {attempt}"
                    )
                    if options.method == "GET":
                        response = await self._session.get(url=options.final_url)
                    elif options.method == "POST":
                        response = await self._session.post(url=options.final_url)
                    r_time = timer.lap()
                    r_status = response.status

                    assert r_status == 200, f"Request failed with status {r_status}"

                    content: str = await response.text()

                    if options.sync_cookies:
                        logger.debug(f"Syncing cookies after {options.final_url}")
                        session_cookies: dict[str, str] = {
                            n: v.value for n, v in response.cookies.items()
                        }
                        self.update_session(cookies=session_cookies)

                    logger.debug(
                        f"Requesting {options.method} {options.final_url} done in {r_time:.3f}s"
                    )

                    return RequestResult(
                        content=content,
                        stats=RequestStats(
                            options=options,
                            status=r_status,
                            time=r_time,
                            size=len(content),
                        ),
                    )

                # except ClientError as ce:
                #     logger.warning(f"ClientError on requesting {options}:\n{ce}")
                except Exception as e:
                    logger.warning(f"{type(e)} on requesting {options}:\n{e}")

        logger.error(f"Request {options} failed after {attempts} attempts")
        return RequestResult(
            stats=RequestStats(
                options=options,
                status=r_status or 0,
                time=r_time or 0.0,
                size=0,
            )
        )
