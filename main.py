import asyncio
from pprint import pprint
import aiofiles

from modules.extractor import FFExtractor
from modules.fetcher import SessionManager, Fetcher
from modules.show_models import Show, ShowType


async def main():
    kp_cookies = FFExtractor.get_cookies("kinopoisk.ru")

    async with SessionManager(cookies=kp_cookies) as sm:
    #     page_fetch = await Fetcher.fetch_page(sm, 1700)

    #     shows_fetch = await Fetcher.batch_fetch_shows(
    #         sm, page_fetch.show_id_container.make_show_list()
    #     )

    # async with aiofiles.open("dump.json", mode="w", encoding="UTF-8") as f:
    #     await f.write("{\n")
    #     await f.writelines(
    #         f"\"{r.show.id}\": {r.show.model_dump_json()},"
    #         for r in shows_fetch.results_by_id.values()
    #         if r.show.info
    #     )
    #     await f.write("}")
        
        pages_fetch = await Fetcher.batch_fetch_pages(sm, range(1, 20), 5)
        for r in pages_fetch.results_by_page.values():
            pprint(r.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
