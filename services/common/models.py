from pydantic import BaseModel, ConfigDict, field_validator, Field
from typing import Optional, Literal, List, Set


class ShowInfo(BaseModel):
    title: str
    rating: float
    rating_count: int
    description: str
    genres: List[str]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("description", mode="before")
    def validate_description(cls, description: str):
        replace_dict = {"\n": " ", "\xa0": " "}
        for s in replace_dict:
            if s in description:
                description = description.replace(s, replace_dict[s])
        return description


class Show(BaseModel):
    id: int
    type: Literal["film", "series"]
    info: Optional[ShowInfo] = None


class ShowIDSets(BaseModel):
    films: Set[int] = Field(default_factory=set)
    series: Set[int] = Field(default_factory=set)

    def update(
        self, films: Optional[Set[int]] = None, series: Optional[Set[int]] = None
    ) -> None:
        self.films.update(films or set())
        self.series.update(series or set())

    @property
    def total_count(self) -> int:
        return len(self.films) + len(self.series)
