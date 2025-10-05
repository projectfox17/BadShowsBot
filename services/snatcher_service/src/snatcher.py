from asyncio import Semaphore, gather
from pydantic import BaseModel, field_serializer
from typing import Optional, List

from common.logger import Logger
from src.session import SessionManager, RequestResult
from common.show_models import ShowIdentifier, ShowModel
from src.parser import Parser

PAGE_URL_BASE = "https://www.kinopoisk.ru/lists/movies"
SHOW_URL_BASE = "https://www.kinopoisk.ru"


class SnatchResult(BaseModel):
    # payload: Optional[ShowModel | List[ShowIdentifier]]
    request_result: RequestResult

    @field_serializer("request_result")
    def serialize_rr_clean(self, request_result: RequestResult, _info):
        return request_result.model_dump(exclude={"content"})


class SnatchSIDsResult(SnatchResult):
    identifier_list: Optional[List[ShowIdentifier]]


class SnatchShowResult(SnatchResult):
    show: Optional[ShowModel]


logger = Logger("Snatcher")


class Snatcher:
    @staticmethod
    async def snatch_identifiers(sm: SessionManager, page: int) -> SnatchSIDsResult:
        """
        Возвращает список `ShowIdentifier` и статистику запроса
        """

        request_result = await sm.request(
            PAGE_URL_BASE, method="GET", params={"sort": "rating", "page": page}
        )
        if request_result.content is None:
            logger.error(f"Failed requesting page {page}")
            return SnatchResult(payload=None, request_result=request_result)

        sid_list: Optional[list[ShowIdentifier]] = await Parser.parse_page(
            request_result.content, page
        )
        if sid_list is None:
            logger.error(f"Failed parsing page {page}")
            return SnatchSIDsResult(identifier_list=None, request_result=request_result)

        return SnatchSIDsResult(identifier_list=sid_list, request_result=request_result)

    @staticmethod
    async def batch_snatch_identifiers(
        sm: SessionManager, page_list: list[int], concurrent: int = 5
    ) -> list[SnatchSIDsResult]:
        """
        Параллельно запускает `snatch_identifiers()`,
        возвращает список списков `ShowIdentifier` и статистики запросов
        """

        async def task(sem: Semaphore, page: int) -> SnatchSIDsResult:
            async with sem:
                return await Snatcher.snatch_identifiers(sm, page)

        sem = Semaphore(concurrent)
        tasks = [task(sem, page) for page in page_list]

        return await gather(*tasks)

    @staticmethod
    async def snatch_show(
        sm: SessionManager, identifier: ShowIdentifier
    ) -> SnatchShowResult:
        """
        Возвращает готовый объект `ShowModel` и статистику запроса
        """
        request_result = await sm.request(
            f"{SHOW_URL_BASE}/{identifier.type.value}/{identifier.id}", method="GET"
        )
        if request_result.content is None:
            logger.error(f"Failed requesting {identifier}")
            return SnatchShowResult(show=None, request_result=request_result)

        show_details = await Parser.parse_show(
            request_result.content, identifier, allow_partial=False
        )

        if show_details is None:
            logger.error(f"Failed parsing {identifier}")
            return SnatchShowResult(show=None, request_result=request_result)

        return SnatchShowResult(
            show=ShowModel(identifier=identifier, details=show_details),
            request_result=request_result,
        )

    @staticmethod
    async def batch_snatch_shows(
        sm: SessionManager, identifier_list: list[ShowIdentifier], concurrent: int = 5
    ) -> list[SnatchShowResult]:
        """
        Параллельно запускает `snatch_show()`,
        возвращает список `ShowModel` и статистики запросов
        """

        async def task(sem: Semaphore, identifier: ShowIdentifier) -> SnatchShowResult:
            async with sem:
                return await Snatcher.snatch_show(sm, identifier)

        sem = Semaphore(concurrent)
        tasks = [task(sem, sid) for sid in identifier_list]
        return await gather(*tasks)
