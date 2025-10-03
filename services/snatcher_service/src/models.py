from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, Dict, List

from common.models import Show, ShowIDSets


class SessionConfig(BaseModel):
    """
    Хранилище cookies и headers для SessionManager
    """

    cookies: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)

    @field_validator("cookies", "headers", mode="before")
    def validate_values(cls, d: Dict) -> Dict[str, str]:
        return {k: str(v) for k, v in d.items()}


class RequestResult(BaseModel):
    content: Optional[str]
    url: str
    status: int
    time: float


class TagDescriptor:
    def __init__(self, name: str, attrs_list: List[Dict[str, str]]):
        self.name = name
        self.attrs_list = attrs_list


class SnatchResult(BaseModel):
    payload: Optional[Show | ShowIDSets]
    request_result: RequestResult

    @field_serializer("request_result")
    def serialize_rr_clean(self, v: RequestResult, _info):
        return v.model_dump(exclude={"content"})
