import os
import getpass
import platform

from _modules.Extractor import OSType


class SystemInfo:

    _username: str = None
    _os_type: OSType = None
    _homedrive: str = None
    _inited: bool = False

    def init(self):

        if self._inited:
            return

        username: str = None
        try:
            username = os.getlogin()
        except OSError:
            username = getpass.getuser()

        if username is None:
            raise Exception("Couldn't fetch username")

        self._username: str = username

        os_type = platform.system()

        if os_type not in OSType:
            raise Exception(f"Unsupported OS type: {os_type}")

        self._os_type: OSType = OSType(os_type)

        if self._os_type == OSType.WINDOWS:
            self._homedrive = os.environ.get("HOMEDRIVE", default="C:")

        self._inited = True

    @classmethod
    def get_username(self) -> str:
        self.init(self)
        return self._username

    @classmethod
    def get_os_type(self) -> OSType:
        self.init(self)
        return self._os_type

    @classmethod
    def get_homedrive(self) -> str | None:
        self.init(self)
        return self._homedrive
