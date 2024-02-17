import urllib.parse
from pathlib import Path
from cx_core.utils import detect_encoding
from abc import abstractmethod
import csv
from .env import env
import xml.etree.ElementTree as ET


class AbstractAdapter:
    def __init__(self):
        self.filename = None
        self.file = None
        self.task = None

    def codec(self):
        return detect_encoding(self.filename)

    def __enter__(self):
        self.file = open(self.filename, 'r', encoding=self.codec())
        self.task = env.progress.add_task(description=f'读取 {self.filename} ...')
        env.progress.wrap_file(self.file, task_id=self.task)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        env.progress.remove_task(self.task)
        return False

    @abstractmethod
    def items(self):
        pass


class CSVAdapter(AbstractAdapter):
    suffix = 'csv'

    def __init__(self, filename):
        super(AbstractAdapter, self).__init__()
        self.filename = Path(filename)

    def items(self):
        reader = csv.DictReader(self.file, fieldnames=['File Name', 'Clip Directory'])
        for row in reader:
            if row['Clip Directory'] == 'Clip Directory':
                env.debug('跳过标题行')
                continue
            source_file = Path(row['Clip Directory'], row['File Name'])
            yield source_file


class TxtAdapter(AbstractAdapter):
    suffix = 'txt'

    def __init__(self, filename):
        super(AbstractAdapter, self).__init__()
        self.filename = Path(filename)

    def items(self):
        for line in self.file:
            yield Path(line.strip().strip('"'))


class XmlAdapter(AbstractAdapter):
    suffix = 'xml'

    def __init__(self, filename):
        super(AbstractAdapter, self).__init__()
        self.filename = filename

    def items(self):
        et = ET.parse(self.file)
        for e in et.iter('pathurl'):
            url = urllib.parse.unquote_plus(e.text)
            if not url.startswith('file:'):
                continue
            path = url.removeprefix('file:')
            yield Path(path)


class FcpXmlAdapter(AbstractAdapter):
    suffix = 'fcpxml'

    def __init__(self, filename):
        super(AbstractAdapter, self).__init__()
        self.filename = filename

    def items(self):
        et = ET.parse(self.file)
        for e in et.iter('media-rep'):
            url = urllib.parse.unquote_plus(e.attrib['src'])
            if not url.startswith('file:'):
                continue
            path = url.removeprefix('file:')
            yield Path(path)


adapters = {'csv': CSVAdapter, 'txt': TxtAdapter, 'xml': XmlAdapter, 'fcpxml': FcpXmlAdapter}
