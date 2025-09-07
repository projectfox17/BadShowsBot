import sqlite3
from pathlib import Path
from configparser import ConfigParser

from _modules.Extractor import OSType, SystemInfo


class FirefoxExtractor:
    _cookies_path: Path = None
    _inited: bool = False

    def init(self):

        if self._inited:
            return

        os_type: OSType = SystemInfo.get_os_type()
        username: str = SystemInfo.get_username()
        ff_path: Path = None

        if os_type == OSType.WINDOWS:
            homedrive: str = SystemInfo.get_homedrive()
            ff_path = (
                Path(homedrive)
                / "/Users"
                / username
                / "AppData"
                / "Roaming"
                / "Mozilla"
                / "Firefox"
            )
        elif os_type == OSType.LINUX:
            ff_path = Path(f"/home/{username}/.mozilla/firefox")

        if ff_path is None:
            raise Exception("Couldn't determine Firefox path")
        
        # print(ff_path)

        profiles_cfg_path: Path = ff_path / "profiles.ini"
        if not profiles_cfg_path.exists():
            raise Exception("Couldn't find Firefox profiles config")

        cp = ConfigParser()
        cp.read(profiles_cfg_path)

        default_profile: str = None
        for sec in cp.sections():
            if str(sec).startswith("Install") and cp.has_option(sec, "Default"):
                default_profile = cp[sec]["Default"]

        if default_profile is None:
            raise Exception("Couldn't get default profile from Firefox profiles config")

        profile_path: Path = ff_path / default_profile
        if not profile_path.exists():
            raise Exception(
                f"{default_profile} dir from Firefox profiles config was not found"
            )
        cookies_path: Path = profile_path / "cookies.sqlite"
        if not cookies_path.exists():
            raise Exception(f"Cookie DB in {default_profile} dir was not found")

        self._cookies_path = cookies_path.resolve()
        self._inited = True

    @classmethod
    def get_cookies(self, domain: str) -> dict[str, str]:
        self.init(self)

        # Workaround for FF DB lock
        tmp_path = self._cookies_path.with_suffix(".tmp.sqlite")
        with open(self._cookies_path, mode="rb") as src, open(
            tmp_path, mode="wb"
        ) as dst:
            dst.write(src.read())

        con = sqlite3.connect(tmp_path)
        cur = con.cursor()

        cur.execute(
            "SELECT name, value FROM moz_cookies WHERE "
            "host LIKE ? AND expiry > strftime('%s','now')",
            (f"%{domain}",),
        )
        cookies: dict[str, str] = {
            str(name): str(value) for name, value in cur.fetchall()
        }

        con.close()
        tmp_path.unlink(missing_ok=True)

        return cookies
