import asyncio
from yarl import URL

from modules.Extractor import FirefoxExtractor
from modules.Parser import *
from modules.ShowData import ShowIDs
from modules.Timer import AsyncTimer


P_RANGE = (1750, 1800)


async def main() -> None:

    cookies = FirefoxExtractor.get_cookies("kinopoisk.ru")

    async with SessionManager(cookies=cookies) as sm:
        sm.get(RequestOptions(URL("https://kinopoisk.ru"), sync_cookies=True))
        parser = Parser(sm)

        async with AsyncTimer() as timer:
            rr_dict = await parser.shows_from_page_range(*P_RANGE, concurrent=10)
            time = timer.elapsed

    show_ids = ShowIDs()
    success_count = 0
    for rr in rr_dict.values():
        if rr.result:
            show_ids.films.update(rr.result.films)
            show_ids.series.update(rr.result.series)
            success_count += 1

    print(
        f"Found {show_ids.total} shows ({len(show_ids.films)} films, {len(show_ids.series)} series) in {time:.3f}s"
    )
    print(f"Page success rate {(success_count / (P_RANGE[1] - P_RANGE[0] + 1) * 100):.1f}%")
    print(f"Show success rate {(show_ids.total / (P_RANGE[1] - P_RANGE[0] + 1) * 2):.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
