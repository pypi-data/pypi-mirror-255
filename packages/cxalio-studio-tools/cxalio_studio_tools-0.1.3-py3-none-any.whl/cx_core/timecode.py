import re
from enum import StrEnum


class Timebase:
    def __init__(self, rate, drop_frame=None):
        self.fps = int(round(rate))
        self.drop_frame = drop_frame if drop_frame is not None else self.fps == float(rate)
        self.input = rate

    def __repr__(self):
        return 'Timebase({0}{1})'.format(self.fps, 'DF' if self.drop_frame else '')

    def __int__(self):
        return self.fps


class TCMode(StrEnum):
    TC = "time_code"
    TS = "time_stamp"


class TimeCode:
    __TEMPLATES = {TCMode.TS: '{0[0]:0>2}:{0[1]:0>2}:{0[2]:0>2}{sep}{0[3]:0>3}',
                   TCMode.TC: '{0[0]:0>2}:{0[1]:0>2}:{0[2]:0>2}{sep}{0[3]:0>2}'}

    def __init__(self, tc_parts: list[int] = None, drop_frame=False, mode=TCMode.TS, custom_sep=None):
        self.__parts = tc_parts if tc_parts else [0, 0, 0, 0]
        self.drop_frame = drop_frame
        self.mode = mode
        self.custom_sep = custom_sep

    @property
    def sep(self):
        if self.custom_sep is not None:
            return self.custom_sep
        if self.mode is TCMode.TS:
            return ','
        return ';' if self.drop_frame else ':'

    @property
    def segments(self):
        return tuple(self.__parts)

    def __str__(self):
        return TimeCode.__TEMPLATES[self.mode].format(self.__parts, sep=self.sep)

    def __repr__(self):
        return 'TimeCode{0}{1}'.format(self.__parts, 'DF' if self.drop_frame else '')

    def __rich__(self):
        sep = '[yellow]:[/yellow]'
        sep2 = f'[yellow]{self.sep}[/yellow]'
        hh, mm, ss, ff = (f'[green]x[/green]' for x in self.__parts)
        return f'{hh}{sep}{mm}{sep}{ss}{sep2}{ff}'


TC_PATTERN = re.compile(r'(\d\d):(\d\d):(\d\d)([:;,\.])(\d\d\d?)')


def is_tc(string: str):
    return TC_PATTERN.fullmatch(string) is not None


_EMPTY_TC_INFO_ = {'tc_parts': (0, 0, 0, 0), 'drop_frame': False, 'mode': TCMode.TS}


def parse_tc_parts(tc: str):
    match = TC_PATTERN.fullmatch(tc.strip())
    if match is None:
        return _EMPTY_TC_INFO_
    groups = match.groups()
    sep = groups[3]
    parts = [int(groups[x]) for x in [0, 1, 2, 4]]
    return {
        'tc_parts': parts,
        'drop_frame': sep == ';',
        'mode': TCMode.TC if sep in ':;' else TCMode.TS
    }


def make_tc_parts(millisecond: int, mode=TCMode.TS, timebase: Timebase = None):
    assert millisecond >= 0
    seconds = millisecond // 1000
    ss = seconds % 60
    minutes = seconds // 60
    mm = minutes % 60
    hours = minutes // 60
    hh = hours % 24
    fff = millisecond % 1000
    if mode is TCMode.TC:
        if timebase is None:
            timebase = Timebase(24, False)
        rate = timebase.fps
        fff = int((millisecond / 1000) * rate) % rate
    tc_parts = [int(x) for x in [hh, mm, ss, fff]]
    return {'tc_parts': tc_parts, 'drop_frame': timebase.drop_frame if timebase else False,
            'mode': mode}
