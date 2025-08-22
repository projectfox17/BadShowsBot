import re
from yarl import URL
from asyncio import Semaphore, gather
from typing import Optional

from modules.Logger import Logger
from defines import GLOBAL_LOGGER_LEVEL

from modules.Parser import SessionManager, RequestOptions, RequestResult
from modules.ShowData import ShowIDs
from modules.Timer import AsyncTimer


logger = Logger("Parser", GLOBAL_LOGGER_LEVEL)


SHOW_LIST_URL = URL("https://www.kinopoisk.ru/lists/movies/")
show_link_pattern = re.compile(r"/(film|series)/(\d+)/")


class Parser:

    def __init__(self, sm: SessionManager) -> None:
        self.session_manager = sm

    async def shows_from_page(self, page: int) -> RequestResult:

        result = ShowIDs()

        async with AsyncTimer() as at:
            text, status = await self.session_manager.get(
                RequestOptions(SHOW_LIST_URL, params={"sort": "rating", "page": page})
            )
            time = at.elapsed

        link_matches: list[tuple[str]] = re.findall(show_link_pattern, text)
        for category, show_id in link_matches:
            show_id = int(show_id)
            if category == "film":
                result.films.add(show_id)
            elif category == "series":
                result.series.add(show_id)

        return RequestResult(
            result=result,
            page=page,
            status=status,
            time=time,
            n_matches=len(link_matches),
            n_shows=result.total,
        )

    async def _task_sfp(
        self, sem: Semaphore, page: int, attempts: int
    ) -> Optional[RequestResult]:

        async with sem:
            for at in range(attempts):
                try:
                    # TODO Add conditions for retry logic based on response stats
                    if at > 0:
                        logger.debug(f"Page {page} request attempt {at + 1}")
                    rr = await self.shows_from_page(page)

                    if rr.status != 200:
                        logger.warning(
                            f"Page {page} request status {rr.status}, retrying"
                        )
                        continue

                    logger.debug(f"Page {page} request done in {rr.time:.3f}s")
                    return rr
                except Exception as e:
                    logger.warning(f"Page {page} request failed with:\n{e}")
            else:
                logger.error(f"Page {page} request unsuccessful")
                return RequestResult(None, page, 0)

    async def shows_from_page_range(
        self, page_from: int, page_to: int, concurrent: int = 5, attempts: int = 3
    ) -> dict[int, Optional[RequestResult]]:

        page_from, page_to = min(page_from, page_to), max(page_from, page_to)
        sem = Semaphore(concurrent)

        tasks = [
            self._task_sfp(sem, page, attempts)
            for page in range(page_from, page_to + 1)
        ]

        rr_list = await gather(*tasks)
        rr_by_page: dict[int, RequestResult] = {}
        for rr in rr_list:
            rr_by_page[rr.page] = rr

        return rr_by_page
