import sys
import logging
from enum import Enum
from modules.utils import DirectEnumMeta


class LoggerLevel(Enum, metaclass=DirectEnumMeta):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:

    def __init__(self, name: str, level=LoggerLevel.DEBUG):
        self._logger = logging.getLogger(name)

        if not self._logger.handlers:
            self._logger.setLevel(level)

            stdout_sh = logging.StreamHandler(sys.stdout)
            stdout_sh.setLevel(level)
            stdout_sh.setFormatter(
                logging.Formatter(
                    fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

            self._logger.addHandler(stdout_sh)
            self._logger.propagate = False

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)
