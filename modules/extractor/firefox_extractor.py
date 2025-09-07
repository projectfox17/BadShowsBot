import sqlite3
from pathlib import Path
from configparser import ConfigParser
from typing import Optional

from modules.extractor import OSType, SystemInfo
from modules.logger import Logger


logger = Logger("Firefox Extractor")


class FFExtractor:
    _cookies_path: Optional[Path] = None

    @classmethod
    def get_cookies(self, domain: str) -> Optional[dict[str, str]]:
        if self._cookies_path is None:
            try:
                os_type = SystemInfo.get_os_type()
                assert os_type is not None, "Couldn't obtain OS type"
                username = SystemInfo.get_username()
                assert username is not None, "Couldn't obtain username"

                if os_type == OSType.LINUX:
                    ff_path = Path(f"/home/{username}/.mozilla/firefox")
                elif os_type == OSType.WINDOWS:
                    hd = SystemInfo.get_homedrive()
                    assert hd is not None, "Couldn't obtain homedrive"
                    ff_path = (
                        Path(hd)
                        / "/Users"
                        / username
                        / "AppData"
                        / "Roaming"
                        / "Mozilla"
                        / "Firefox"
                    )
                assert ff_path.exists(), f"Couldn't find Firefox directory at {ff_path}"

                cfg_path = ff_path / "profiles.ini"
                assert cfg_path.exists(), f"Couldn't find profiles config at {cfg_path}"

                cfg = ConfigParser()
                cfg.read(cfg_path)
                default_profile: str = None
                for section in cfg.sections():
                    if str(section).startswith("Install") and cfg.has_option(
                        section, "Default"
                    ):
                        default_profile = cfg[section]["Default"]
                assert (
                    default_profile is not None
                ), "Couldn't find default profile in config"

                profile_path = ff_path / default_profile
                assert (
                    profile_path.exists()
                ), f"Couldn't find profile {default_profile} directory"

                cookies_path = profile_path / "cookies.sqlite"
                assert (
                    cookies_path.exists()
                ), f"Couldn't find cookies DB at {cookies_path}"
                self._cookies_path = cookies_path.resolve()

            except Exception as e:
                logger.error(f"Failed obtaining Firefox cookies DB\n{e}")
                return None

        try:
            tmp_path = self._cookies_path.with_suffix(".tmp.sqlite")
            with open(self._cookies_path, mode="rb") as src, open(
                tmp_path, mode="wb"
            ) as dest:
                dest.write(src.read())

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

        except Exception as e:
            logger.error(f"Failed reading Firefox cookies for {domain}:\n{e}")
            return None

        return cookies
