import re
from abc import abstractmethod
from os import PathLike
from pathlib import Path

from docx import Document
from functools import cached_property

from cx_core.timepoint import TimePoint
from cx_core.utils import detect_encoding
from .subtitle import Subtitle


class AbstractSubtitleLoader:
    def __init__(self, source: str | PathLike):
        self.source = Path(source)
        self.file = None

    @cached_property
    def encoding(self):
        return detect_encoding(self.source)

    def __enter__(self):
        self.file = open(self.source, 'r', encoding=self.encoding)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        return False

    @abstractmethod
    def subtitles(self):
        pass


class TxtLoader(AbstractSubtitleLoader):
    MILLISECOND_PER_CHAR = 120
    MIN_DURATION_PER_LINE = 2000
    TS_PATTERN = r'\s*\d{2}:\d{2}:\d{2}.\d{3}\s*'

    def __init__(self, filename):
        super(TxtLoader, self).__init__(filename)
        self.__last_point = TimePoint(0)

    def subtitles(self):
        for a in self.file:
            content = re.sub(self.TS_PATTERN, '', a)
            duration = len(content) * TxtLoader.MILLISECOND_PER_CHAR
            if duration < TxtLoader.MIN_DURATION_PER_LINE:
                duration = TxtLoader.MIN_DURATION_PER_LINE
            start = self.__last_point
            end = start + TimePoint(duration)
            yield Subtitle(start=start, end=end, content=content)
            self.__last_point = end


class SrtLoader(AbstractSubtitleLoader):
    HEAD_LINE = re.compile(r'^\d+$')
    TIME_LINE = re.compile(r'^(\d\d:\d\d:\d\d[,.]\d\d\d) --> (\d\d:\d\d:\d\d[,.]\d\d\d)$')

    def __int__(self, filename):
        super(SrtLoader, self).__init__(filename)

    def subtitles(self):
        content, start, end = '', None, None
        state = None
        for a in self.file:
            line = a.strip()
            if not state:
                if SrtLoader.HEAD_LINE.fullmatch(line):
                    content = ''
                    start = None
                    end = None
                    state = 'started'
            elif state == 'started':
                match = SrtLoader.TIME_LINE.fullmatch(line)
                if match:
                    start = TimePoint.from_timestamp(match.group(1))
                    end = TimePoint.from_timestamp(match.group(2))
                    state = 'timed'
            elif state == 'timed':
                if line:
                    content += line
                else:
                    yield Subtitle(start=start, end=end, content=content)
                    state = None


class WordLoader(AbstractSubtitleLoader):
    MILLISECOND_PER_CHAR = 120
    MIN_DURATION_PER_LINE = 2000
    TS_PATTERN = r'\s*\d{2}:\d{2}:\d{2}.\d{3}\s*'

    def __init__(self, filename):
        super(WordLoader, self).__init__(filename)
        self.__last_point = TimePoint(0)
        self.document = None

    def __enter__(self):
        self.document = Document(str(self.source.absolute()))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def subtitles(self):
        for a in self.document.paragraphs:
            content = re.sub(self.TS_PATTERN, '', a.text)
            duration = len(content) * TxtLoader.MILLISECOND_PER_CHAR
            if duration < TxtLoader.MIN_DURATION_PER_LINE:
                duration = TxtLoader.MIN_DURATION_PER_LINE
            start = self.__last_point
            end = start + TimePoint(duration)
            yield Subtitle(start=start, end=end, content=content)
            self.__last_point = end


class TTMLLoader(AbstractSubtitleLoader):
    PATTERN = r'<p begin=\"(\d\d:\d\d:\d\d.\d\d\d)\" end=\"(\d\d:\d\d:\d\d.\d\d\d)\">(.*?)</p>\s'
    REPLACEMENTS = {
        '<br/>': '\n',
        '&quot;': '"'
    }

    def __init__(self, filename):
        super(TTMLLoader, self).__init__(filename)

    def subtitles(self):
        total = self.file.read()
        pat = re.compile(self.PATTERN, re.DOTALL)
        for match in pat.finditer(total):
            start = TimePoint.from_timestamp(match.group(1))
            end = TimePoint.from_timestamp(match.group(2))
            content = match.group(3)
            for k, v in self.REPLACEMENTS.items():
                content = content.replace(k, v)
            yield Subtitle(
                start=start, end=end, content=content
            )
