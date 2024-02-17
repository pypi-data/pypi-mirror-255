from dataclasses import dataclass
from functools import cached_property

from cx_core.timepoint import TimePoint


@dataclass(order=True)
class Subtitle:
    start: TimePoint
    end: TimePoint
    content: str

    def __rich__(self):
        return f'''[yellow]{self.start.timestamp} [cyan]-->[/cyan] {self.end.timestamp}[/yellow]\
[cyan] : [/cyan][blue]{self.content}[blue]'''

    @cached_property
    def duration(self):
        return self.end - self.start
