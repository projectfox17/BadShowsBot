import os
import getpass
import platform
from enum import Enum
from typing import Optional

from modules.logger import Logger


logger = Logger("System Info")


class OSType(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    # MACOS = "Darwin"


class SystemInfo:
    _username: Optional[str] = None
    _os_type: Optional[OSType] = None
    _homedrive: Optional[str] = None

    @classmethod
    def get_username(self) -> Optional[str]:
        if self._username is None:
            try:
                username = os.getlogin()
            except OSError:
                username = getpass.getuser()
            if username is None:
                logger.error("Couldn't get username")
                return None
            self._username = username
        return self._username

    @classmethod
    def get_os_type(self) -> Optional[OSType]:
        if self._os_type is None:
            os_name = platform.system()
            if os_name not in OSType:
                logger.error("Unsupported OS type")
                return None
            self._os_type = OSType(os_name)
        return self._os_type

    @classmethod
    def get_homedrive(self) -> Optional[str]:
        if self._homedrive is None:
            if self._os_type is None:
                self.get_os_type()
            if self._os_type != OSType.WINDOWS:
                logger.error(f"Can't get homedrive on {self._os_type.name}")
                return None
            self._homedrive = os.environ.get("HOMEDRIVE", default="C:\\")
        return self._homedrive
