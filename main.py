import asyncio

from modules.Extractor import FirefoxExtractor
from modules.KinopoiskWorker import SessionManager, KinopoiskWorker, PageRequestStats
from modules.ShowData import ShowIDs


async def main() -> None:

    cookies = FirefoxExtractor.get_cookies("kinopoisk.ru")

    async with SessionManager(cookies=cookies) as sm:
        show_ids, stats_list = await KinopoiskWorker.bulk_get_page_shows(sm, 1700, 1800, concurrent=15)

    anomalies = list(filter(lambda ps: ps.shows < 50, stats_list))

    if anomalies:
        anomalies.sort(key=lambda ps: ps.page)
        print(f"{len(anomalies)} pages were parsed partially:")

        for ps in anomalies:
            print(f"{ps.page}: {ps.shows} shows, {ps.size} content length")


if __name__ == "__main__":
    asyncio.run(main())
