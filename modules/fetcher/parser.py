import re
from bs4 import BeautifulSoup, Tag
from typing import Optional
from enum import Enum

from modules.show_models import ShowInfo, ShowIDContainer, Show
from modules.fetcher import (
    TagParams,
    PageParseStats,
    PageParseResult,
    ShowParseStats,
    ShowParseResult,
)
from modules.async_timer import AsyncTimer
from modules.logger import Logger


logger = Logger("Parser")


class KPTagParams(Enum):
    title = TagParams(
        name="span", attrs_list=[{"data-tid": "75209b22"}, {"data-tid": "2da92aed"}]
    )
    rating = TagParams(name="span", attrs_list=[{"data-tid": "939058a8"}])
    rating_count = TagParams(name="span", attrs_list=[{"class": "styles_count__mJ4RS"}])
    description = TagParams(name="p", attrs_list=[{"class": "styles_paragraph__V0fA2"}])
    genre_box = TagParams(name="div", attrs_list=[{"data-tid": "28726596"}])

    page_show_box = TagParams(
        name="div", attrs_list=[{"class": "styles_content__2fRe6"}]
    )
    page_show_link = TagParams(
        name="a", attrs_list=[{"class": "base-movie-main-info_link__K161e"}]
    )
    # page_show_rating = TagParams(...)


def get_soup(text: str, soup_parser: str = "html.parser") -> BeautifulSoup:
    return BeautifulSoup(text, soup_parser)


def find_tag(
    root: BeautifulSoup | Tag, params: KPTagParams, logger_str: Optional[str] = None
) -> Optional[Tag]:
    for attrs in params.value.attrs_list:
        tag = root.find(params.value.name, attrs=attrs)
        if tag:
            return tag
    logger.warning(
        f"{logger_str if logger_str else ""}Couldn't find {params.name} "
        f"<{params.value.name}> with {params.value.attrs_list}"
    )
    return None


def find_all_tags(
    root: BeautifulSoup | Tag, params: KPTagParams, logger_str: Optional[str] = None
) -> Optional[list[Tag]]:
    for attrs in params.value.attrs_list:
        tag_list = root.find_all(params.value.name, attrs=attrs)
        if tag_list:
            return list(tag_list)
    logger.warning(
        f"{logger_str if logger_str else ""}Couldn't find {params.name} "
        f"<{params.value.name}> with {params.value.attrs_list}"
    )
    return None


class Parser:
    @staticmethod
    async def parse_page(content: str, page: Optional[int] = None) -> PageParseResult:
        page_str = f"Page {page} " if page else ""

        async with AsyncTimer() as timer:
            try:
                soup = get_soup(content)
                container = ShowIDContainer()

                show_boxes = find_all_tags(soup, KPTagParams.page_show_box, page_str)
                for show_box in show_boxes or []:
                    show_link = find_tag(show_box, KPTagParams.page_show_link, page_str)
                    if show_link and "href" in show_link.attrs:
                        show_type, show_id = show_link.attrs["href"][1:-1].split("/")
                        show_id = int(show_id)
                        if show_type == "film":
                            container.films.add(show_id)
                        elif show_type == "series":
                            container.series.add(show_id)

                parse_time = timer.lap()

            except Exception as e:
                logger.error(f"{page_str}Failed parsing\n{e}")
                return PageParseResult(
                    show_id_container=None,
                    stats=PageParseStats(show_count=len(show_boxes), time=parse_time),
                )

        return PageParseResult(
            show_id_container=container,
            stats=PageParseStats(show_count=container.total_count, time=parse_time),
        )

    @staticmethod
    async def parse_show(
        content: str, show: Optional[Show] = None, allow_partial: bool = False
    ) -> ShowParseResult:
        show_str = f"{show.type.name}/{show.id} " if show else ""

        async with AsyncTimer() as timer:
            try:
                soup = get_soup(content, "lxml")

                title_tag = find_tag(soup, KPTagParams.title, show_str)
                title = None
                if title_tag:
                    title: str = title_tag.text.strip()
                    year_match = re.search(r"\s\(\d{4}\)$", title)
                    if year_match:
                        title = title[: year_match.start()]

                rating_tag = find_tag(soup, KPTagParams.rating)
                rating = None
                if rating_tag:
                    try:
                        rating = float(rating_tag.text)
                    except Exception as r_exc:
                        logger.error(
                            f"{show_str}Failed parsing rating value {rating_tag.text}:\n{r_exc}"
                        )

                rating_count_tag = find_tag(soup, KPTagParams.rating_count, show_str)
                rating_count = None
                if rating_count_tag:
                    try:
                        rating_count = int(
                            "".join(re.findall(r"(\d)\s?", rating_count_tag.text))
                        )
                    except Exception as rc_exc:
                        logger.error(
                            f"{show_str}Failed parsing rating count value "
                            f"{rating_count_tag.text}:\n{rc_exc}"
                        )

                description_tag = find_tag(soup, KPTagParams.description, show_str)
                description = description_tag.text.strip() if description_tag else None

                genre_box = find_tag(soup, KPTagParams.genre_box, show_str)
                genres = None
                if genre_box:
                    genre_tags = genre_box.find_all("a")
                    if genre_tags:
                        genres = [tag.text.strip() for tag in genre_tags]
                        if "слова" in genres:
                            genres.remove("слова")
                    else:
                        logger.warning(f"{show_str}Couldn't find genres in genre box")

                parse_time = timer.lap()

                if not allow_partial and any(
                    field is None
                    for field in (title, rating, rating_count, description, genres)
                ):
                    raise LookupError("Couldn't find some field values, check logs")

            except Exception as e:
                logger.error(f"{show_str}Failed parsing\n{e}")
                return ShowParseResult(
                    stats=ShowParseStats(time=timer.lap()), show_info=None
                )

        return ShowParseResult(
            stats=ShowParseStats(time=parse_time),
            show_info=ShowInfo(
                title=title or "",
                rating=rating or 0.0,
                rating_count=rating_count or 0,
                description=description or "",
                genres=genres or [],
            ),
        )
