import asyncio
import aiofiles

from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Any, Dict, List

from common.show_models import *
from src.session import SessionManager, SessionConfig
from src.snatcher import Snatcher, SnatchResult


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sm

    async with aiofiles.open(
        "config/session_config.json", mode="r", encoding="UTF-8"
    ) as src:
        session_config = SessionConfig.model_validate_json(await src.read())

    sm = SessionManager(session_config)
    yield
    sm.close_session()


app = FastAPI(lifespan=lifespan)


@app.get("/snatch_page")
async def snatch_page(
    page: int = 1,
    as_shows: bool = False,
    include_none: bool = False,
    concurrent: int = 5,
) -> Dict[str, Any]:
    page_result = await Snatcher.snatch_identifiers(sm, page)

    if as_shows and page_result.identifier_list:
        show_results = [
            show_res
            for show_res in await Snatcher.batch_snatch_shows(
                sm, page_result.identifier_list, concurrent
            )
            if include_none or show_res.show
        ]
        return {
            "status": "ok" if show_results else "fail",
            "mode": "shows",
            "result": show_results,
        }

    return {
        "status": "ok" if page_result.identifier_list else "fail",
        "mode": "identifiers",
        "result": page_result,
    }


@app.get("/batch_snatch_pages")
async def batch_snatch_pages(
    page_from: int,
    page_to: int,
    as_shows: bool = False,
    include_none: bool = False,
    concurrent: int = 5,
) -> Dict[str, Any]:
    page_list = list(
        range(page_from, page_to + 1, 1)
        if page_to > page_from
        else range(page_from, page_to - 1, -1)
    )
    page_results = await Snatcher.batch_snatch_identifiers(sm, page_list, concurrent)

    if as_shows:
        sid_list: List[ShowIdentifier] = []
        for page_res in page_results:
            if page_res.identifier_list:
                sid_list += page_res.identifier_list

        show_results = [
            show_res
            for show_res in await Snatcher.batch_snatch_shows(sm, sid_list, concurrent)
            if include_none or show_res.show
        ]
        return {
            "status": "ok" if show_results else "fail",
            "mode": "shows",
            "result": show_results,
        }

    return {
        "status": (
            "ok"
            if any(page_res.identifier_list for page_res in page_results)
            else "fail"
        ),
        "mode": "identifiers",
        "result": [
            page_res
            for page_res in page_results
            if include_none or page_res.identifier_list
        ],
    }


if __name__ == "__main__":
    # asyncio.run(snatch_page())
    pass
