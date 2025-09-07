import asyncio, aiofiles
from pprint import pprint

from modules.fetcher import RequestOptions, SessionManager
from _modules.Extractor import FirefoxExtractor
from modules.fetcher import Parser, ShowParseResult
from modules.show_models import Show, ShowType


async def main():
    kp_cookies = FirefoxExtractor.get_cookies("kinopoisk.ru")

    show = Show(id=4696000, type=ShowType.SERIES)

    async with SessionManager(cookies=kp_cookies) as sm:
        rr = await sm.request(
            RequestOptions(
                method="GET",
                url=f"https://www.kinopoisk.ru/" f"{show.type.value}/" f"{show.id}/",
            )
        )

    spr: ShowParseResult = await Parser.parse_show(rr.content, show, allow_partial=True)
    show.info = spr.show_info
    pprint(show.model_dump())
    pprint(spr.model_dump()["stats"])


if __name__ == "__main__":
    asyncio.run(main())
