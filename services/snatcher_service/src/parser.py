import re
from bs4 import BeautifulSoup, Tag
from typing import Optional, Literal
from enum import Enum

from common.logger import Logger
from common.models import ShowInfo, ShowIDSets
from src.models import TagDescriptor


logger = Logger("Parser")


class KinopoiskTags(Enum):
    title = TagDescriptor(
        name="span", attrs_list=[{"data-tid": "75209b22"}, {"data-tid": "2da92aed"}]
    )
    rating = TagDescriptor(name="span", attrs_list=[{"data-tid": "939058a8"}])
    rating_count = TagDescriptor(
        name="span", attrs_list=[{"class": "styles_count__mJ4RS"}]
    )
    description = TagDescriptor(
        name="p", attrs_list=[{"class": "styles_paragraph__V0fA2"}]
    )
    genre_box = TagDescriptor(name="div", attrs_list=[{"data-tid": "28726596"}])

    page_show_box = TagDescriptor(
        name="div", attrs_list=[{"class": "styles_content__2fRe6"}]
    )
    page_show_link = TagDescriptor(
        name="a", attrs_list=[{"class": "base-movie-main-info_link__K161e"}]
    )


def get_soup(text: str, soup_parser: str = "html.parser") -> BeautifulSoup:
    return BeautifulSoup(text, soup_parser)


def find_tag(source: BeautifulSoup | Tag, desc: TagDescriptor) -> Optional[Tag]:
    for attrs in desc.attrs_list:
        tag = source.find(desc.name, attrs=attrs)
        if tag:
            return tag
    return None


def find_all_tags(
    source: BeautifulSoup | Tag, desc: TagDescriptor
) -> Optional[list[Tag]]:
    for attrs in desc.attrs_list:
        tags = source.find_all(desc.name, attrs=attrs)
        if tags:
            return list(tags)
    return None


class Parser:
    @staticmethod
    async def parse_page(content: str, page: int) -> Optional[ShowIDSets]:
        try:
            logger.debug(f"Parsing page {page}")
            soup = get_soup(content)

            boxes = find_all_tags(soup, KinopoiskTags.page_show_box.value)
            if boxes is None:
                logger.warning(f"Failed to find show boxes on page {page}")
                return None

            id_sets = ShowIDSets()
            for box in boxes:
                link = find_tag(box, KinopoiskTags.page_show_link.value)
                if link is None or "href" not in link.attrs:
                    logger.warning(f"Abnormal show box on page {page}: {box.attrs}")
                    continue

                show_type, show_id = link.attrs["href"][1:-1].split("/")
                show_id = int(show_id)
                if show_type == "film":
                    id_sets.films.add(show_id)
                elif show_type == "series":
                    id_sets.series.add(show_id)

            logger.debug(f"Done parsing page {page}")
            return id_sets

        except Exception as e:
            logger.error(f"Failed parsing page {page}: {e}")
            return None

    @staticmethod
    async def parse_show(
        content: str,
        show_id: int,
        show_type: Literal["film", "series"],
        allow_partial: bool = False,
    ) -> Optional[ShowInfo]:
        try:
            logger.debug(f"Parsing {show_type} {show_id}")
            soup = get_soup(content)

            title_tag = find_tag(soup, KinopoiskTags.title.value)
            if title_tag:
                title: str = title_tag.text.strip()
                year_match = re.search(r"\s\(\d{4}\)$", title)
                if year_match:
                    title = title[: year_match.start()]
            else:
                logger.warning(f"Failed fetching title for {show_type} {show_id}")
                title = None

            rating_tag = find_tag(soup, KinopoiskTags.rating.value)
            if rating_tag and re.match(r"^\d+\.\d+$", rating_tag.text):
                rating = float(rating_tag.text)
            else:
                logger.warning(f"Failed fetching rating for {show_type} {show_id}")
                rating = None

            r_count_tag = find_tag(soup, KinopoiskTags.rating_count.value)
            if r_count_tag:
                r_count = int("".join(re.findall(r"(\d)\s?", r_count_tag.text)))
            else:
                logger.warning(
                    f"Failed fetching rating count for {show_type} {show_id}"
                )
                r_count = None

            desc_tag = find_tag(soup, KinopoiskTags.description.value)
            if desc_tag:
                desc = desc_tag.text.strip()
            else:
                logger.warning(f"Failed fetching description for {show_type} {show_id}")
                desc = None

            genre_box = find_tag(soup, KinopoiskTags.genre_box.value)
            if genre_box:
                genre_tags = genre_box.find_all("a")
                if genre_tags:
                    genres = [tag.text.strip() for tag in genre_tags]
                    if "слова" in genres:
                        genres.remove("слова")
                else:
                    logger.warning(f"Abnormal genre box in {show_type} {show_id}")
                    genres = None
            else:
                logger.warning(f"Failed fetching genres in {show_type} {show_id}")
                genres = None

            if not allow_partial and any(
                field is None for field in (title, rating, r_count, desc, genres)
            ):
                raise LookupError(
                    f"Couldn't fetch all fields for {show_type} {show_id}"
                )

            logger.debug(f"Done parsing {show_type} {show_id}")
            return ShowInfo(
                title=title or "",
                rating=rating or 0.0,
                rating_count=r_count or 0,
                description=desc or "",
                genres=genres or [],
            )

        except Exception as e:
            logger.error(f"Failed parsing {show_type} {show_id}: {e}")
            return None
