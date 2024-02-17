import re

from .subtitle import Subtitle


class SubtitleFormatter:
    def __init__(self, **kwargs):
        self.replacements = {'\t': ' '}
        self.remove_tags = True

        self.normal_strip = True
        self.strip_quotes = True
        self.extra_strips = ''

        self.remove_empty_lines = True
        self.shrink_long_spaces = True
        self.shrink_long_quotes = True

        self.remove_empty_subtitles = True
        self.remove_zero_duration_subtitles = True

        self.__dict__.update(kwargs)

    def __basic_content_cleaning(self, content: str):
        result = content
        for k, v in self.replacements.items():
            result = result.replace(k, v)
        result = re.sub(r'\r\n', r'\n', result)
        return result

    @staticmethod
    def __remove_tags(content: str):
        return re.sub(
            r'<(\w+)>([^<>]*)</\1>',
            r'\2',
            content
        )

    def __strip(self, content: str):
        result = str(content)
        while True:
            current = result
            if self.normal_strip:
                current = current.strip()
            if self.strip_quotes:
                current = current.strip('\'"‘“”’')
            if self.extra_strips:
                current = current.strip(self.extra_strips)
            if current == result:
                break
            result = current
            current = None
        return result

    @staticmethod
    def __remove_empty_lines(content: str):
        result = re.sub(r'\n\s+', r'\n', content)
        return result

    @staticmethod
    def __shrink_long_spaces(content: str):
        result = re.sub(r' +', r' ', content)
        return result

    @staticmethod
    def __shrink_long_quotes(content: str):
        result = re.sub(r'([\'\"‘“”’])+', r'\1', content)
        return result

    def format_subtitle(self, subtitle: Subtitle):
        content = self.__basic_content_cleaning(subtitle.content)
        content = self.__strip(content)
        if self.remove_tags:
            content = self.__remove_tags(content)
        if self.remove_empty_lines:
            content = self.__remove_empty_lines(content)
        if self.shrink_long_spaces:
            content = self.__shrink_long_spaces(content)
        if self.shrink_long_quotes:
            content = self.__shrink_long_quotes(content)
        subtitle.content = content
        return subtitle

    def is_subtitle_legal(self, subtitle: Subtitle):
        if self.remove_empty_subtitles and not subtitle.content:
            return False
        if self.remove_zero_duration_subtitles and subtitle.duration == 0:
            return False
        return True

    def format_sequence(self, subtitles: list[Subtitle]):
        result = [self.format_subtitle(sub) for sub in subtitles if self.is_subtitle_legal(sub)]
        result = sorted(result, key=lambda x: x.start)
        return result

    def __call__(self, sth: Subtitle | list[Subtitle]):
        if isinstance(sth, list):
            return self.format_sequence(sth)
        elif isinstance(sth, Subtitle):
            return self.format_subtitle(sth)
        return sth
