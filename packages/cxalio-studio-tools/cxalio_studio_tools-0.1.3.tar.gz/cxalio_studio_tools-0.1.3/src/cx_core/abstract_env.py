from .app_logger import AppLogger, LogLevel


class AbstractEnv:
    def __init__(self):
        self._logger = AppLogger()

    def print(self, *objs):
        self._logger.print(*objs, level=LogLevel.NORMAL)

    def debug(self, *objs):
        self._logger.print(*objs, level=LogLevel.DEBUG)

    def info(self, *objs):
        self._logger.print(*objs, level=LogLevel.INFO)

    def error(self, *objs):
        self._logger.print(*objs, level=LogLevel.ERROR)

    def warning(self, *objs):
        self._logger.print(*objs, level=LogLevel.WARNING)

    def critical(self, *objs):
        self._logger.print(*objs, level=LogLevel.CRITICAL)

    @property
    def log_level(self):
        return self._logger.level

    @log_level.setter
    def log_level(self,level):
        self._logger.level = level
