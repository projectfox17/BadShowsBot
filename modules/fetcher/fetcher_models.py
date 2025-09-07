from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Dict, Literal, List
from yarl import URL

from modules.show_models import ShowIDContainer, ShowInfo, Show


# Request input & output


class RequestOptions(BaseModel):
    # TODO: do something with __get_pydantic_core_schema__ for yarl.URL
    url: URL
    method: Literal["GET", "POST"]
    params: Dict[str, any] = Field(default_factory=dict)
    sync_cookies: bool = Field(default=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("url", mode="before")
    def validate_url(cls, url):
        if isinstance(url, str):
            return URL(url)
        if isinstance(url, URL):
            return url
        raise TypeError(f"URL must be yarl.URL or str, {type(url)} was given")

    @property
    def final_url(self) -> URL:
        return self.url.update_query(self.params)


class RequestStats(BaseModel):
    options: RequestOptions
    status: int
    time: float = Field(default=0.0)
    size: int = Field(default=0)


class RequestResult(BaseModel):
    request_stats: RequestStats
    content: Optional[str] = Field(default=None)


# Parsing params & outputs


class TagParams(BaseModel):
    name: str
    attrs_list: List[Dict[str, str]]

    # def __str__(self) -> str:
    #     return f"{self.name}:\n{"\n".join(attrs for attrs in self.attrs_list)}"


class PageParseStats(BaseModel):
    show_count: int
    time: float = Field(default=0.0)


class PageParseResult(BaseModel):
    stats: PageParseStats
    show_id_container: Optional[ShowIDContainer] = Field(default=None)


class ShowParseStats(BaseModel):
    time: float = Field(default=0.0)


class ShowParseResult(BaseModel):
    stats: ShowParseStats
    show_info: Optional[ShowInfo] = Field(default=None)


# Fetcher output


class PageFetchResult(BaseModel):
    request_stats: RequestStats
    parse_stats: PageParseStats
    show_id_container: Optional[ShowIDContainer] = Field(default=None)


class BulkPageFetchResult(BaseModel):
    results_by_page: Dict[int, PageParseResult] = Field(default_factory=dict)
    total_time: float = Field(default=0.0)

    @property
    def final_container(self) -> ShowIDContainer:
        container = ShowIDContainer()
        for result in self.results_by_page.values():
            if result.show_id_container:
                container.merge(result.show_id_container)
        return container


class ShowFetchResult(BaseModel):
    request_stats: RequestStats
    parse_stats: ShowParseStats
    show: Optional[Show] = Field(default=None)


class BulkShowFetchResult(BaseModel):
    results_by_id: Dict[int, ShowParseResult] = Field(default_factory=dict)
    total_time: float = Field(default=0.0)

    @property
    def results_list(self) -> list[ShowInfo]:
        return [
            result.show_info
            for result in self.results_by_id.values()
            if result.show_info
        ]
