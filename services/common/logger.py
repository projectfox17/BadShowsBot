import sys
import logging
from enum import Enum


class LoggerLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    def __init__(self, name: str, level=LoggerLevel.DEBUG):
        self._logger = logging.getLogger(name)

        if not self._logger.handlers:
            self._logger.setLevel(level.value)

            sh_stdout = logging.StreamHandler(sys.stdout)
            sh_stdout.setLevel(level.value)
            sh_stdout.setFormatter(
                logging.Formatter(
                    # fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                    fmt="%(levelname)-8s %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            self._logger.addHandler(sh_stdout)

            self._logger.propagate = False

    def debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)
