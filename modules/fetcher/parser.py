import re
from bs4 import BeautifulSoup
from typing import Literal

from modules.show_models import ShowInfo, ShowIDContainer
from modules.fetcher import (
    PageParseStats,
    PageParseResult,
    ShowParseStats,
    ShowParseResult,
)
from modules.async_timer import AsyncTimer
from modules.logger import Logger
from defines import SOUP_SHOW_ARGS


logger = Logger("Parser")


def get_soup(text: str, soup_parser: str = "html.parser") -> BeautifulSoup:
    return BeautifulSoup(text, soup_parser)


class Parser:
    @staticmethod
    def parse_page(content: str) -> PageParseResult:
        pass

    @staticmethod
    async def parse_show(
        content: str, show_id: int, show_type: Literal["FILM", "SERIES"]
    ) -> ShowParseResult:
        async with AsyncTimer() as timer:
            soup = get_soup(content, "lxml")

            # Look for title
            title_tag = soup.find(*SOUP_SHOW_ARGS["title"])
            if not title_tag:
                raise LookupError(
                    f"{show_id}: Couldn't find title tag with {SOUP_SHOW_ARGS["title"]}"
                )
            title = title_tag.text

            # Look for rating
            rating_tag = soup.find(*SOUP_SHOW_ARGS["rating"])
            if not rating_tag:
                raise LookupError(
                    f"{show_id}: Couldn't find rating tag with {SOUP_SHOW_ARGS["rating"]}"
                )
            rating = rating_tag.text

            # Look for rating count
            rating_count_tag = soup.find(*SOUP_SHOW_ARGS["rating_count"])
            if not rating_count_tag:
                raise LookupError(
                    f"{show_id}: Couldn't find rating count tag with {SOUP_SHOW_ARGS["rating_count"]}"
                )
            rating_count = rating_count_tag.text
            rating_count = "".join(re.findall(r"(\d)\s?", rating_count))

            # Look for description
            description_tag = soup.find(*SOUP_SHOW_ARGS["description"])
            if not description_tag:
                raise LookupError(
                    f"{show_id}: Couldn't find description tag with {SOUP_SHOW_ARGS["description"]}"
                )
            description = description_tag.text

            # Look for genres
            genre_box = soup.find(
                SOUP_SHOW_ARGS["genres"][0], attrs=SOUP_SHOW_ARGS["genres"][1]
            )
            if not genre_box:
                raise LookupError(
                    f"{show_id}: Couldn't find genre tags with {SOUP_SHOW_ARGS["genres"]}"
                )
            genre_tags = genre_box.find_all("a")
            genres = [tag.text for tag in genre_tags]

            parse_time = timer.lap()

        return ShowParseResult(
            stats=ShowParseStats(show_id=show_id, time=parse_time),
            show_info=ShowInfo(
                show_id=show_id,
                show_type=show_type,
                title=title,
                rating=rating,
                rating_count=rating_count,
                description=description,
                genres=genres,
            ),
        )
