from functools import lru_cache, total_ordering

from .timecode import *


@total_ordering
class TimePoint:
    def __init__(self, millisecond=0):
        self._millisecond = int(millisecond)

    @property
    def millisecond(self) -> int:
        return self._millisecond

    @property
    def second(self) -> float:
        return self._millisecond / 1000

    @property
    @lru_cache()
    def timestamp(self) -> TimeCode:
        parts = make_tc_parts(self._millisecond)
        return TimeCode(**parts)

    @classmethod
    def from_second(cls, second: float = 0):
        return cls(round(second * 1000))

    @classmethod
    def from_timestamp(cls, ts: str):
        assert is_tc(ts)
        tc_info = parse_tc_parts(ts)
        h, m, s, f = tc_info['tc_parts']
        hh = h * 60 * 60
        mm = m * 60
        second = hh + mm + s
        milli = second * 1000 + f
        return cls(milli)

    def __int__(self):
        return self._millisecond

    def __add__(self, other):
        return TimePoint(self._millisecond + int(other))

    def __iadd__(self, other):
        self._millisecond += int(other)

    def __isub__(self, other):
        self._millisecond -= int(other)

    def __sub__(self, other):
        return TimePoint(self._millisecond - int(other))

    def __eq__(self, other):
        return self._millisecond == int(other)

    def __lt__(self, other):
        return self._millisecond < int(other)

    def __hash__(self):
        return hash(self._millisecond)

    def __repr__(self):
        return f'TimePoint({self.millisecond})'
