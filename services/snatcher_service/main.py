import asyncio, aiofiles
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Any, Dict, List

from common.models import Show, ShowIDSets
from src.session import SessionManager
from src.models import SessionConfig, RequestResult, SnatchResult
from src.snatcher import Snatcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    global snatcher
    async with aiofiles.open(
        "config/session_config.json", mode="r", encoding="UTF-8"
    ) as sconf_file:
        session_config = SessionConfig.model_validate_json(await sconf_file.read())
    snatcher = Snatcher(SessionManager(session_config))
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/snatch_page")
async def snatch_page(
    page: int = 1, as_shows: bool = False, concurrent: int = 5
) -> Dict[str, str | SnatchResult | List[SnatchResult]]:
    page_result = await snatcher.snatch_page_ids(page)

    if as_shows and page_result.payload:
        show_results = [
            show_res
            for show_res in await snatcher.batch_snatch_shows(
                page_result.payload, concurrent
            )
            if show_res.payload
        ]
        return {"status": "ok" if show_results else "fail", "result": show_results}

    return {
        "status": "ok" if page_result.payload else "fail",
        "result": page_result,
    }


@app.get("/batch_snatch_pages")
async def batch_snatch_pages(
    page_from: int, page_to: int, as_shows: bool = False, concurrent: int = 5
) -> Dict[str, str | List[SnatchResult]]:
    rng = list(
        range(page_from, page_to + 1, 1)
        if page_to > page_from
        else range(page_from, page_to - 1, -1)
    )
    page_results = await snatcher.batch_snatch_page_ids(rng, concurrent)

    if as_shows:
        show_results = []
        for page_res in page_results:
            if page_res.payload:
                show_results += [
                    show_res
                    for show_res in await snatcher.batch_snatch_shows(
                        page_res.payload, concurrent
                    )
                    if show_res.payload
                ]
        return {"status": "ok" if show_results else "fail", "result": show_results}

    return {
        "status": (
            "ok" if any(page_res.payload for page_res in page_results) else "fail"
        ),
        "result": page_results,
    }


if __name__ == "__main__":
    # asyncio.run(snatch_page())
    pass
