import asyncio
from pprint import pprint

from modules.extractor import FFExtractor
from modules.fetcher import RequestOptions, SessionManager
from modules.fetcher import Parser, ShowParseResult
from modules.show_models import Show, ShowType


async def main():
    kp_cookies = FFExtractor.get_cookies("kinopoisk.ru")
    pprint(kp_cookies)

    show = Show(id=679486, type=ShowType.FILM)

    async with SessionManager(cookies=kp_cookies) as sm:
        rr = await sm.request(
            RequestOptions(
                method="GET",
                url=f"https://www.kinopoisk.ru/{show.type.value}/{show.id}/",
            )
        )

    spr: ShowParseResult = await Parser.parse_show(rr.content, show, allow_partial=False)
    show.info = spr.show_info
    pprint(show.model_dump())
    # pprint(spr.model_dump()["stats"])


if __name__ == "__main__":
    asyncio.run(main())
