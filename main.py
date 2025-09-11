import asyncio
from pprint import pprint

from modules.extractor import FFExtractor
from modules.storage import PROJECT_STORAGE_NODES
from modules.fetcher import SessionConfig, SessionManager, RequestOptions
from modules.logger import Logger
from defines import DEFAULT_HEADERS


logger = Logger("Main")


async def main():
    # fb_sc_file = PROJECT_STORAGE_NODES["FB_SESSION_CONFIG"]
    sc_file = PROJECT_STORAGE_NODES["SESSION_CONFIG"]

    # if sc_file.runtime_created:
    #     logger.warning("Session config file was not present, loading fallback config")
    #     sc = SessionConfig.model_validate_json(await fb_sc_file.a_read())
    # else:
    #     sc = SessionConfig.model_validate_json(await sc_file.a_read())

    sm = SessionManager(config=SessionConfig(cookies=FFExtractor.get_cookies("kinopoisk.ru"), headers=DEFAULT_HEADERS))
    await sm.request(
        RequestOptions(
            url="https://kinopoisk.ru",
            method="GET",
            # params={"sort": "rating", "page": 1},
            sync_config=True,
        )
    )
    await sm.close_session()

    await sc_file.a_write(sm.config.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
