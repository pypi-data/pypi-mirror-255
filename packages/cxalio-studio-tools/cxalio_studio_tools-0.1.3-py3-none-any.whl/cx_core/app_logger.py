from enum import IntEnum

from rich.console import Console
from rich.text import Text


class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    NORMAL = 999


class AppLogger:
    DEFAULT_HEADER_STYLES = {LogLevel.DEBUG: 'green', LogLevel.INFO: 'cyan', LogLevel.WARNING: 'purple',
                             LogLevel.ERROR: 'magenta', LogLevel.CRITICAL: 'red bold', LogLevel.NORMAL: 'blue'}

    def __init__(self, console=None, level=LogLevel.WARNING, header='::'):
        self._console = Console() if console is None else console
        self.level = level
        self.header = header
        self.header_styles = AppLogger.DEFAULT_HEADER_STYLES

    def styled_header(self, level=LogLevel.NORMAL):
        return Text(self.header, style=self.header_styles[level])

    def force_print(self, *objects, level=LogLevel.NORMAL):
        self._console.print(self.styled_header(level), *objects,
                            # style=AppLogger.DEFAULT_HEADER_STYLES[level],
                            markup=True, highlight=True)

    def print(self, *objects, level=LogLevel.NORMAL):
        if level < self.level:
            return
        else:
            self.force_print(*objects, level=level)
