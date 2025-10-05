import re
from bs4 import BeautifulSoup, Tag
from typing import Optional
from enum import Enum

from common.logger import Logger
from common.show_models import ShowIdentifier, ShowDetails


REPLACE = {"\n": " ", "\xa0": " "}


class TagDescriptor:
    def __init__(self, name: str, attrs_list: list[dict[str, str]]):
        self.name = name
        self.attrs_list = attrs_list


class KPTags(Enum):
    PShowBox = TagDescriptor(
        name="div", attrs_list=[{"class": "styles_content__2fRe6"}]
    )
    PShowLink = TagDescriptor(
        name="a", attrs_list=[{"class": "base-movie-main-info_link__K161e"}]
    )

    STitle = TagDescriptor(
        name="span", attrs_list=[{"data-tid": "75209b22"}, {"data-tid": "2da92aed"}]
    )
    SRating = TagDescriptor(name="span", attrs_list=[{"data-tid": "939058a8"}])
    SRatingCount = TagDescriptor(
        name="span", attrs_list=[{"class": "styles_count__mJ4RS"}]
    )
    SDescription = TagDescriptor(
        name="p", attrs_list=[{"class": "styles_paragraph__V0fA2"}]
    )
    SGenreBox = TagDescriptor(name="div", attrs_list=[{"data-tid": "28726596"}])


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


logger = Logger("Parser")


class Parser:
    @staticmethod
    async def parse_page(content: str, page: int) -> Optional[list[ShowIdentifier]]:
        try:
            logger.debug(f"Parsing page {page}...")
            soup = get_soup(content)

            boxes = find_all_tags(soup, KPTags.PShowBox.value)
            if boxes is None:
                logger.warning(f"Failed to find show boxes on page {page}")
                return None

            sid_list: list[ShowIdentifier] = []
            for box in boxes:
                link = find_tag(box, KPTags.PShowLink.value)
                if link is None or "href" not in link.attrs:
                    logger.warning(f"Abnormal show box on page {page}: {box.attrs}")
                    continue

                show_type, show_id = link.attrs["href"][1:-1].split("/")
                sid_list.append(ShowIdentifier(id=show_id, type=show_type))

            logger.debug(f"Done parsing page {page}")
            return sid_list

        except Exception as e:
            logger.error(f"Failed parsing page {page}: {e}")
            return None

    @staticmethod
    async def parse_show(
        content: str,
        identifier: ShowIdentifier,
        allow_partial: bool = False,
    ) -> Optional[ShowDetails]:
        try:
            logger.debug(f"Parsing {identifier}")
            soup = get_soup(content)

            title_tag = find_tag(soup, KPTags.STitle.value)
            if title_tag:
                title: str = title_tag.text.strip()
                year_match = re.search(r"\s\(\d{4}\)$", title)
                if year_match:
                    title = title[: year_match.start()]
            else:
                logger.warning(f"Failed fetching title for {identifier}")
                title = None

            rating_tag = find_tag(soup, KPTags.SRating.value)
            if rating_tag and re.match(r"^\d+\.\d+$", rating_tag.text):
                rating = float(rating_tag.text)
            else:
                logger.warning(f"Failed fetching rating for {identifier}")
                rating = None

            rating_count_tag = find_tag(soup, KPTags.SRatingCount.value)
            if rating_count_tag:
                rating_count = int(
                    "".join(re.findall(r"(\d)\s?", rating_count_tag.text))
                )
            else:
                logger.warning(f"Failed fetching rating count for {identifier}")
                rating_count = None

            description_tag = find_tag(soup, KPTags.SDescription.value)
            if description_tag:
                description = description_tag.text.strip()
                for k, v in REPLACE.items():
                    if k in description:
                        description = description.replace(k, v)
            else:
                logger.warning(f"Failed fetching description for {identifier}")
                description = None

            genre_box = find_tag(soup, KPTags.SGenreBox.value)
            if genre_box:
                genre_tags = genre_box.find_all("a")
                if genre_tags:
                    genres = [tag.text.strip() for tag in genre_tags]
                    if "слова" in genres:
                        genres.remove("слова")
                else:
                    logger.warning(f"Abnormal genre box in {identifier}")
                    genres = None
            else:
                logger.warning(f"Failed fetching genres in {identifier}")
                genres = None

            if not allow_partial and any(
                field is None
                for field in (title, rating, rating_count, description, genres)
            ):
                raise LookupError(f"Couldn't fetch all fields for {identifier}")

            logger.debug(f"Done parsing {identifier}")
            return ShowDetails(
                title=title or "",
                rating=rating or 0.0,
                rating_count=rating_count or 0,
                description=description or "",
                genres=genres or [],
            )

        except Exception as e:
            logger.error(f"Failed parsing {identifier}: {e}")
            return None
