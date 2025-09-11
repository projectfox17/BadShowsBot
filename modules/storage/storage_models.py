import aiofiles
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator
from enum import Enum
from typing import Literal

from modules.logger import Logger


logger = Logger("Storage")


class StorageNodeType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


class BaseStorageNode(BaseModel):
    name: str
    path: Path
    type: StorageNodeType
    required_to_exist: bool = False
    runtime_created: bool = Field(default=False, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_model(self):
        self.path = self.path.resolve()

        if not self.path.exists():
            if self.required_to_exist:
                s = f"Required {self.type} {self.name} at {self.path} not found!"
                logger.critical(s)
                # exit(-1)
                raise FileNotFoundError(s)

            self.create()
            logger.debug(f"{self.type.value} {self.name} was created at {self.path}")
            self.runtime_created = True

        if self.type is StorageNodeType.DIRECTORY and not self.path.is_dir():
            s = f"{self.name} expected to be a directory, is a file"
            logger.error(s)
            # self.type = StorageNodeType.FILE
            raise ValueError(s)
        if self.type is StorageNodeType.FILE and not self.path.is_file():
            s = f"{self.name} expected to be a file, is a directory"
            logger.error(s)
            # self.type = StorageNodeType.DIRECTORY
            raise ValueError(s)

        return self

    def create(self):
        raise NotImplementedError


class DirectoryStorageNode(BaseStorageNode):
    type: Literal[StorageNodeType.DIRECTORY] = StorageNodeType.DIRECTORY

    def create(self):
        self.path.mkdir(parents=True, exist_ok=True)

    @property
    def contents(self) -> list[Path]:
        return list(self.path.iterdir())


class FileStorageNode(BaseStorageNode):
    type: Literal[StorageNodeType.FILE] = StorageNodeType.FILE

    def create(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()

    async def a_read(self, mode="r", enc="UTF-8") -> str | bytes:
        async with aiofiles.open(self.path, mode=mode, encoding=enc) as src:
            content = await src.read()
        return content

    async def a_write(self, content: str | bytes, mode="w", enc="UTF-8"):
        async with aiofiles.open(self.path, mode=mode, encoding=enc) as dest:
            await dest.write(content)
