import aiohttp
from typing import Optional

from modules.Parser import RequestOptions


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

    async def close_session(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self, *args):
        return self

    async def __aexit__(self, *args):
        await self.close_session()

    def update_headers(
        self, headers: dict[str, str], overwrite_conflicts: bool = True
    ) -> None:

        for name, value in headers.items():
            if not overwrite_conflicts and name in self._headers:
                continue
            self._headers[name] = value
        self._session.headers.update(self._headers)

    def update_cookies(
        self, cookies: dict[str, str], overwrite_conflicts: bool = True
    ) -> None:

        for name, value in cookies.items():
            if not overwrite_conflicts and name in self._cookies:
                continue
            self._cookies[name] = value
        self._session.cookie_jar.update_cookies(self._cookies)

    async def get(self, options: RequestOptions) -> tuple[str, int]:
        """
        Performs a GET request with specified options
        Returns response text and status
        """

        async with self._session.get(options.url, params=options.params) as resp:

            if options.sync_cookies:
                session_cookies: dict[str, str] = {
                    str(n): str(v.value) for n, v in resp.cookies.items()
                }
                self.update_cookies(session_cookies)

            return await resp.text(), resp.status

    async def post(self, options: RequestOptions) -> tuple[str, int]:
        """
        Performs a POST request with specified options
        Returns response text and status
        """

        async with self._session.post(options.url, params=options.params) as resp:

            if options.sync_cookies:
                session_cookies: dict[str, str] = {
                    str(n): str(v.value) for n, v in resp.cookies.items()
                }
                self.update_cookies(session_cookies)

            return await resp.text(), resp.status
