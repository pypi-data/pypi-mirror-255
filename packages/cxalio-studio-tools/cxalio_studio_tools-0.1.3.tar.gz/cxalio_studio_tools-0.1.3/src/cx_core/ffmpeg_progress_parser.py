import re
from pathlib import Path


class FFmpegProgressParser:
    DURATION_RX = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})")
    CURRENT_RX = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}")
    FILENAME_RX = re.compile(r"from '(.*)':")
    FPS_RX = re.compile(r"(\d{2}\.\d{2}|\d{2}) fps")

    @staticmethod
    def _seconds(hours, minutes, seconds, ms=0):
        millisecond = float(ms) / 100
        ss = (int(hours) * 60 + int(minutes)) * 60 + int(seconds)
        return float(ss) + millisecond

    def __init__(self) -> None:
        self.started = False
        self.duration = None
        self.fps = None
        self.filename = None
        self.current = None

    def __call__(self, line: str):
        self.started = True
        if self.duration is None:
            self.duration = self.get_duration(line)

        if self.filename is None:
            self.filename = self.get_filename(line)

        self.fps = self.get_fps(line)
        self.current = self.get_current(line)

    def get_duration(self, line: str):
        search = self.DURATION_RX.search(line)
        if search is not None:
            return self._seconds(*search.groups())
        return None

    def get_fps(self, line: str):
        search = self.FPS_RX.search(line)
        if search is not None:
            return round(float(search.group(1)))
        return None

    def get_filename(self, line: str):
        search = self.FILENAME_RX.search(line)
        if search is not None:
            p = Path(search.group(1))
            return p.name
        return None

    def get_current(self, line: str):
        search = self.CURRENT_RX.search(line)
        if search is not None:
            return self._seconds(*search.groups())
        return None
