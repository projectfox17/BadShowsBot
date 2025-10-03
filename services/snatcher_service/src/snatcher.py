from asyncio import Semaphore, gather
from typing import Optional, Literal

from common.logger import Logger
from common.models import Show, ShowIDSets
from src.session import SessionManager
from src.parser import Parser
from src.models import RequestResult, SnatchResult

PAGE_URL_BASE = "https://www.kinopoisk.ru/lists/movies"
SHOW_URL_BASE = "https://www.kinopoisk.ru"
logger = Logger("Snatcher")


class Snatcher:
    def __init__(self, sm: SessionManager):
        self.sm = sm
        logger.info("Snatcher up")

    async def snatch_page_ids(self, page: int) -> SnatchResult:
        reqr = await self.sm.request(
            PAGE_URL_BASE, method="GET", params={"sort": "rating", "page": page}
        )
        if reqr.content is None:
            logger.error(f"Failed requesting page {page}")
            return SnatchResult(payload=None, request_result=reqr)

        show_ids: Optional[ShowIDSets] = await Parser.parse_page(reqr.content, page)
        if show_ids is None:
            logger.error(f"Failed parsing page {page}")
            return SnatchResult(payload=None, request_result=reqr)
        return SnatchResult(payload=show_ids, request_result=reqr)

    async def batch_snatch_page_ids(
        self, page_list: list[int], concurrent: int = 5
    ) -> list[SnatchResult]:

        async def task(sem: Semaphore, page: int) -> SnatchResult:
            async with sem:
                return await self.snatch_page_ids(page)

        sem = Semaphore(concurrent)
        tasks = [task(sem, page) for page in page_list]
        
        return await gather(*tasks)

    async def snatch_show(
        self, show_id: int, show_type: Literal["film", "series"]
    ) -> SnatchResult:
        reqr = await self.sm.request(
            f"{SHOW_URL_BASE}/{show_type}/{show_id}", method="GET"
        )
        if reqr.content is None:
            logger.error(f"Failed requesting {show_type} {show_id}")
            return SnatchResult(payload=None, request_result=reqr)

        show_info = await Parser.parse_show(
            reqr.content, show_id, show_type, allow_partial=False
        )
        
        if show_info is None:
            logger.error(f"Failed parsing {show_type} {show_id}")
            return SnatchResult(payload=None, request_result=reqr)
        
        return SnatchResult(payload=Show(id=show_id, type=show_type, info=show_info), request_result=reqr)

    async def batch_snatch_shows(
        self, show_ids: ShowIDSets, concurrent: int = 5
    ) -> list[SnatchResult]:

        async def task(
            sem: Semaphore, show_id: int, show_type: Literal["film", "series"]
        ) -> SnatchResult:
            async with sem:
                return await self.snatch_show(show_id, show_type)

        sem = Semaphore(concurrent)
        tasks = [task(sem, film_id, "film") for film_id in show_ids.films] + [
            task(sem, series_id, "series") for series_id in show_ids.series
        ]
        return [res for res in await gather(*tasks) if res.payload]
