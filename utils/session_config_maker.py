import sqlite3
import json
from configparser import ConfigParser
import os, getpass, platform
from pathlib import Path

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,image/svg+xml,image/png,image/jpeg,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


def make_session_config_file() -> None:
    user, os_type = getpass.getuser(), platform.system()

    if os_type == "Windows":
        print("Long live Billy (Herrington)")
        hd = os.getenv("HOMEDRIVE", default="C:\\")
        ff_path = (
            Path(hd) / "/Users" / user / "AppData" / "Roaming" / "Mozilla" / "Firefox"
        )
    elif os_type == "Linux":
        print("Go touch grass ffs")
        ff_path = Path(f"/home/{user}/.mozilla/firefox")
    else:
        print("Darwin award")
        return

    cfg_path = ff_path / "profiles.ini"
    if not cfg_path.exists():
        print("Couldn't find Firefox config")
        return

    cfg = ConfigParser()
    cfg.read(cfg_path)

    profile = None
    for sec in cfg.sections():
        if str(sec).startswith("Install") and cfg.has_option(sec, "Default"):
            profile = cfg[sec]["Default"]
            break

    if profile is None:
        print("Couldn't find default profile in config")
        return

    db_path = ff_path / profile / "cookies.sqlite"
    if not db_path.exists():
        print(f"Couldn't find cookies DB in {profile}")
        return

    dummy_path = db_path.with_suffix(".tmp.sqlite")
    with open(db_path, mode="rb") as src, open(dummy_path, mode="wb") as dest:
        dest.write(src.read())

    con = sqlite3.connect(dummy_path)
    cur = con.cursor()
    cur.execute(
        "SELECT name, value FROM moz_cookies WHERE "
        "host LIKE ? AND expiry > strftime('%s','now')",
        ("%kinopoisk.ru",),
    )
    cookies = {str(n): str(v) for n, v in cur.fetchall()}
    con.close()
    dummy_path.unlink(missing_ok=True)
    if not cookies:
        print("Failed fetching kinopoisk cookies from db")

    session_cfg_path = (
        Path(__file__).parents[1].resolve() / "config" / "session_config.json"
    )
    if session_cfg_path.exists():
        print("Backing up old config")
        bak_path = session_cfg_path.with_suffix(".bak.json")
        bak_path.touch()
        with open(session_cfg_path, mode="rb") as src, open(
            bak_path, mode="wb"
        ) as dest:
            dest.write(src.read())
    else:
        session_cfg_path.parent.mkdir(parents=True, exist_ok=True)
        session_cfg_path.touch()

    with open(session_cfg_path, mode="w", encoding="UTF-8") as dest:
        dest.write(
            json.dumps({"headers": default_headers, "cookies": cookies}, indent=4)
        )
    print(f"Wrote session config to {session_cfg_path}")


if __name__ == "__main__":
    make_session_config_file()
