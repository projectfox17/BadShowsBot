import asyncio, aiofiles
from pprint import pprint

from modules.fetcher import RequestOptions, SessionManager
from _modules.Extractor import FirefoxExtractor
from modules.fetcher import Parser, ShowParseResult


async def main():
    kp_cookies = FirefoxExtractor.get_cookies("kinopoisk.ru")

    async with SessionManager(cookies=kp_cookies) as sm:
        rr = await sm.request(
            RequestOptions(method="GET", url="https://www.kinopoisk.ru/series/5611838/")
        )
    # pprint(rr.request_stats.model_dump())

    spr: ShowParseResult = await Parser.parse_show(rr.content, 8420095, "FILM")

    pprint(spr.show_info.model_dump())
    # print(spr.show_info.description)


if __name__ == "__main__":
    asyncio.run(main())
