from yarl import URL
from asyncio import Semaphore, gather

from modules.KinopoiskWorker import (
    RequestOptions,
    PageRequestStats,
    SessionManager,
    Parser,
)
from modules.ShowData import ShowIDs
from modules.Timer import AsyncTimer
from modules.Logger import Logger


logger = Logger("KPWorker")


class KinopoiskWorker:

    @staticmethod
    async def bulk_get_page_shows(
        sm: SessionManager,
        page_from: int,
        page_to: int,
        concurrent: int = 5,
        attempts: int = 3,
    ) -> tuple[ShowIDs, list[PageRequestStats]]:

        async def task(
            semaphore: Semaphore, page: int
        ) -> tuple[ShowIDs, PageRequestStats]:

            logger.debug(f"Parsing page {page}")

            async with AsyncTimer() as timer:
                content, req_stats = await sm.get(
                    RequestOptions(
                        url=URL("https://www.kinopoisk.ru/lists/movies/"),
                        params={"sort": "rating", "page": page},
                    ),
                    attempts,
                )

                if content is None:
                    logger.error(
                        f"Parsing page {page} failed: couldn't complete request, check logs"
                    )
                    return None, None

                show_ids = Parser.get_page_shows(content)
                time = timer.elapsed
                page_stats = PageRequestStats(req_stats)
                page_stats.page = page
                page_stats.shows = show_ids.total

            logger.debug(
                f"Done parsing page {page} in {time:.3f}s, found {show_ids.total} shows "
                f"({len(show_ids.films)} films, {len(show_ids.series)} series)"
            )
            return show_ids, page_stats

        logger.debug(f"Parsing pages {page_from}-{page_to} started")

        sem = Semaphore(concurrent)
        tasks = [task(sem, page) for page in range(page_from, page_to + 1)]

        async with AsyncTimer() as timer:
            results: list[tuple[ShowIDs, PageRequestStats] | None] = await gather(
                *tasks
            )
            time = timer.elapsed

        show_ids = ShowIDs()
        stats_list: list[PageRequestStats] = []

        for page_ids, page_stats in results:

            if page_ids is None:
                continue

            show_ids.films.update(page_ids.films)
            show_ids.series.update(page_ids.series)
            stats_list.append(page_stats)

        logger.debug(
            f"Done parsing pages {page_from}-{page_to} in {time:.3f}s, found {show_ids.total} shows "
            f"({len(show_ids.films)} films, {len(show_ids.series)} series)"
        )
        return show_ids, stats_list
