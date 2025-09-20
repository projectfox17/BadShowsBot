from enum import Enum
from pydantic import BaseModel, ConfigDict, field_serializer
from pathlib import Path
from typing import Literal


class NodeType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


class NodeSpec(BaseModel):
    """
    Класс-скелет, хранит поля для генерации
    фактических нод в Storage
    """

    name: str
    type: NodeType
    relative_path: Path
    required: bool = False
    missing_ok: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # @field_serializer
    # def serialize_type(cls, v: NodeType):
    #     return v.value


class NodeGeneric(BaseModel):
    name: str
    path: Path
    type: NodeType

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FileNode(NodeGeneric):
    type: Literal[NodeType.FILE] = NodeType.FILE


class DirectoryNode(NodeGeneric):
    type: Literal[NodeType.DIRECTORY] = NodeType.DIRECTORY
