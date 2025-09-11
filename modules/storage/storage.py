import sys
from pathlib import Path

from modules.storage import FileStorageNode, DirectoryStorageNode
from defines import ROOT_NAME
from modules.logger import Logger


logger = Logger("Storage")

# IMPORTANT
# This module MUST be located at <project_root>/modules/storage

CURRENT_FILEPATH = Path(__file__)
ROOT_PATH = CURRENT_FILEPATH.parents[2].resolve()


def storage_check():
    if ROOT_PATH.name != ROOT_NAME:
        logger.critical(f"Could not resolve project root")
        if CURRENT_FILEPATH != ROOT_PATH / "modules" / "storage" / "storage.py":
            logger.critical(
                f"Storage module misplacement:\n"
                f"Got {CURRENT_FILEPATH}\nExpected .../{ROOT_NAME}/modules/storage/storage.py"
            )
            sys.exit(-1)
        logger.critical(
            f"Project root name mismatch:\nGot {ROOT_PATH.name}\nExpected {ROOT_NAME}"
        )
        sys.exit(-1)


PROJECT_STORAGE_NODES: dict[str, FileStorageNode | DirectoryStorageNode] = {
    "FB_SESSION_CONFIG": FileStorageNode(
        name="fallback_session_config",
        path=ROOT_PATH / "config" / "fb_session_config.json",
        required_to_exist=True,
    ),
    "SESSION_CONFIG": FileStorageNode(
        name="session_config", path=ROOT_PATH / "config" / "session_config.json"
    ),
}
