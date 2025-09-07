import asyncio
from pprint import pprint

from modules.fetcher import RequestOptions, RequestStats, RequestResult, SessionManager
from _modules.Extractor import FirefoxExtractor


async def main():
    kp_cookies = FirefoxExtractor.get_cookies("kinopoisk.ru")

    async with SessionManager(cookies=kp_cookies) as sm:
        rr = await sm.request(
            RequestOptions(
                method="GET",
                url="https://kinopoisk.ru/lists/movies",
                params={"sort": "rating", "page": 1700},
            )
        )
    pprint(rr.request_stats.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
