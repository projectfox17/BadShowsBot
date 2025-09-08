import asyncio
from pprint import pprint
from time import sleep

from modules.extractor import FFExtractor
from modules.fetcher import SessionManager, Fetcher
from modules.show_models import Show, ShowType


async def main():
    kp_cookies = FFExtractor.get_cookies("kinopoisk.ru")

    async with SessionManager(cookies=kp_cookies) as sm:
        page_fetch = await Fetcher.fetch_page(sm, 1)

        shows: list[Show] = []
        for film_id in page_fetch.show_id_container.films:
            show_fetch = await Fetcher.fetch_show(
                sm, film_id, ShowType.FILM, allow_partial=True
            )
            shows.append(show_fetch.show)
            sleep(2)
        for series_id in page_fetch.show_id_container.films:
            show_fetch = await Fetcher.fetch_show(
                sm, series_id, ShowType.SERIES, allow_partial=True
            )
            sleep(2)
            shows.append(show_fetch.show)

    for s in shows:
        if s:
            pprint(s.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
