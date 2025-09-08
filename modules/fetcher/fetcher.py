from asyncio import Semaphore, gather
from typing import Optional

from modules.fetcher import (
    SessionManager,
    RequestOptions,
    Parser,
    PageParseStats,
    ShowParseStats,
    PageFetchResult,
    ShowFetchResult,
    BatchPageFetchResult,
    BatchShowFetchResult,
)
from modules.show_models import Show, ShowType
from defines import KP_PAGE_URL_BASE, KP_SHOW_URL_BASE
from modules.async_timer import AsyncTimer
from modules.logger import Logger


logger = Logger("Fetcher")


class Fetcher:

    @staticmethod
    async def fetch_page(
        sm: SessionManager, page_n: int, attempts: int = 3
    ) -> PageFetchResult:
        try:
            request_result = await sm.request(
                RequestOptions(
                    method="GET",
                    url=KP_PAGE_URL_BASE,
                    params={"sort": "rating", "page": page_n},
                ),
                attempts,
            )
            if request_result.content is None:
                logger.error(f"Page {page_n} fetch failed on requesting, check logs")
                return PageFetchResult(
                    request_stats=request_result.stats,
                    parse_stats=PageParseStats(show_count=0, time=0.0),
                    show_id_container=None,
                )

            parse_result = await Parser.parse_page(request_result.content, page_n)
            if parse_result.show_id_container is None:
                logger.error(f"Page {page_n} fetch failed on parsing, check logs")

        except Exception as e:
            logger.error(f"Failed fetching page {page_n}\n{e}")
            return PageFetchResult(
                request_stats=request_result.stats,
                parse_stats=...,
                show_id_container=None,
            )

        return PageFetchResult(
            request_stats=request_result.stats,
            parse_stats=parse_result.stats,
            show_id_container=parse_result.show_id_container,
        )

    @staticmethod
    async def fetch_show(
        sm: SessionManager,
        dummy_show: Show,
        attempts: int = 3,
        allow_partial: bool = False,
    ) -> ShowFetchResult:
        show_str = f"{dummy_show.type.value}/{dummy_show.id}"
        try:
            request_result = await sm.request(
                RequestOptions(
                    method="GET",
                    url=f"{KP_SHOW_URL_BASE}/{dummy_show.type.value}/{dummy_show.id}",
                ),
                attempts,
            )
            if request_result.content is None:
                logger.error(f"Show {show_str} fetch failed on requesting, check logs")
                return ShowFetchResult(
                    request_stats=request_result.stats,
                    parse_stats=ShowParseStats(time=0.0),
                    show=None,
                )

            show = dummy_show.model_copy()
            parse_result = await Parser.parse_show(
                request_result.content, show, allow_partial=allow_partial
            )
            if parse_result.show_info is None:
                logger.error(f"Show {show_str} fetch failed on parsing, check logs")
            show.info = parse_result.show_info

        except Exception as e:
            return ShowFetchResult(
                request_stats=request_result.stats,
                parse_stats=parse_result.stats,
                show=None,
            )

        return ShowFetchResult(
            request_stats=request_result.stats,
            parse_stats=parse_result.stats,
            show=show,
        )

    @staticmethod
    async def batch_fetch_shows(
        sm: SessionManager,
        dummy_show_list: list[Show],
        concurrent: int = 5,
        attempts: int = 3,
        allow_partial: bool = False,
    ) -> BatchShowFetchResult:

        async def show_task(
            sem: Semaphore,
            dummy_show,
            sm=sm,
            attempts=attempts,
            allow_partial=allow_partial,
        ) -> ShowFetchResult:
            async with sem:
                result = await Fetcher.fetch_show(
                    sm, dummy_show, attempts, allow_partial
                )
                return result

        sem = Semaphore(concurrent)
        tasks = [show_task(sem, dummy_show) for dummy_show in dummy_show_list]

        results = await gather(*tasks)
        t_time = sum([r.request_stats.time + r.parse_stats.time for r in results])

        return BatchShowFetchResult(
            results_by_id={r.show.id: r for r in results if r.show}, total_time=t_time
        )
