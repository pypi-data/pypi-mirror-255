import pkgutil
from argparse import ArgumentParser

from rich.columns import Columns
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich_argparse import RichHelpFormatter

from cx_core import AbstractApp, DataPackage, LogLevel
from cx_core.folder_expander import FolderExpander
from cx_subtitle import SubtitleFormatter
from cx_subtitle.loader import *
from cx_subtitle.saver import *
from .env import env
from .exceptions import *


class SubConvApp(AbstractApp):
    __loader_classes = {
        '.srt': SrtLoader,
        '.txt': TxtLoader,
        '.docx': WordLoader,
        '.ttml': TTMLLoader
    }

    __saver_classes = {
        'srt': SrtSaver,
        'txt': TxtSaver,
        'word': WordSaver,
        'excel': ExcelSaver,
        'csv': CsvSaver
    }

    __suffixes = {
        'txt': '.txt',
        'word': '.docx',
        'excel': '.xlsx',
        'csv': '.csv',
        'srt': '.srt',
        'ttml': '.ttml',
        'rtf': '.rtf'
    }

    def __init__(self):
        super(SubConvApp, self).__init__()

        _parser = ArgumentParser(prog='subconv',
                                 description=f'批量提取台词本，支持的格式包括{' '.join(str(x) for x in self.__loader_classes.keys())}',
                                 epilog='Designed by Cxalio',
                                 formatter_class=RichHelpFormatter, exit_on_error=False)
        _parser.add_argument('--format', '-f', dest='format', default='txt',
                             choices=self.__saver_classes.keys(),
                             help='指定输出格式')

        _parser.add_argument('--encoding', '-c', dest='encoding', default='auto',
                             help='设定输出编码')

        _parser.add_argument('-o', '--output-folder', dest='target_folder', default=None,
                             help='制定输出目录')

        _parser.add_argument('-t', '--time', dest='keep_time', action='store_true',
                             help='尽量保留时间信息')

        _parser.add_argument('--bypass-formatter', dest='bypass_formatter', default=False,
                             action='store_true', help='跳过默认的内容检查器，使用原样输出')

        _parser.add_argument('--debug', '-d', action='store_true', dest='debug',
                             help='调试模式')

        _parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                             help='干转模式，不执行写入操作')

        _parser.add_argument('--man', help='显示详细的说明',
                             dest='show_man', action='store_true')

        _parser.add_argument('sources', nargs='*',
                             help='需要转换的文件')

        self.parser = _parser
        self.args = None

    def __enter__(self):
        _args = self.parser.parse_args()
        self.args = DataPackage(**vars(_args))
        env.log_level = LogLevel.DEBUG if self.args.debug else LogLevel.WARNING
        env.info('Initialized ...')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        env.info('Bye ~')
        return False

    def is_loadable(self, source):
        suffix = Path(source).suffix.lower()
        return suffix in self.__loader_classes

    def make_loader(self, source) -> AbstractSubtitleLoader:
        source = Path(source)
        env.info(f'开始构建 loader <- {source}')
        if not source.is_file():
            raise ValueError('这玩意儿不是文件')
        loader_class = self.__loader_classes.get(source.suffix.lower())
        loader = loader_class(source) if loader_class else None
        return loader

    @staticmethod
    def show_man():
        data = pkgutil.get_data('subconv', 'help.md').decode('utf-8')
        env.console.print(Markdown(data))

    @property
    def target_suffix(self):
        suffix = self.__suffixes.get(str(self.args.format).lower())
        return suffix if suffix else '.txt'

    @property
    def target_encoding(self):
        return 'utf-8' if self.args.encoding == 'auto' else self.args.encoding

    @staticmethod
    def print_subtitles(subtitles):
        panels = (
            Panel(Text(x.content, style='blue'),
                  title=Text(str(x.start.timestamp), style='yellow'),
                  subtitle=Text(str(x.end.timestamp), style='green'),
                  title_align='left',
                  subtitle_align='right',
                  expand=True)
            for x in subtitles)
        env.print(Columns(panels, expand=True, equal=True))

    def make_saver(self, source) -> AbstractSubtitleSaver:
        source = Path(source)
        target = source.with_suffix(self.target_suffix)
        env.info(f'开始构建 saver -> {target.name}')
        if self.args.target_folder:
            target = Path(self.args.target_folder) / target.name
            env.info(f'检测到指定的目标文件夹,已更新目标："{target.absolute()}"')
        saver_class = self.__saver_classes.get(self.args.format, TxtSaver)
        saver = saver_class(target, keep_time=self.args.keep_time)
        saver.encoding = self.target_encoding
        return saver

    def do_job(self, source):
        env.info(f'开始执行任务{source}')
        source = Path(source)
        if not self.is_loadable(source):
            env.error(f'{source}的格式无法读取，将跳过任务')
            return

        if source.suffix == self.target_suffix:
            env.error(f'[yellow]{source.name}[/yellow] 源文件和目标文件格式相同，跳过处理。')
            return

        with self.make_loader(source) as loader:
            subtitles = [x for x in loader.subtitles()]

        if not self.args.bypass_formatter:
            formatter = SubtitleFormatter()
            subtitles = formatter(subtitles)

        if self.args.debug:
            self.print_subtitles(subtitles)

        if self.args.dry_run:
            env.print(f'[yellow]{source.name}[/yellow] 已成功读取，[red]干转模式跳过输出[/red] ...')
            return

        with self.make_saver(source) as saver:
            target = saver.target
            for sbt in subtitles:
                saver.write(sbt)

        env.print(f'[yellow]{target.name}[/yellow] ... [green]转换完成[/green]')

    def sources(self):
        if not self.args.sources:
            return []
        s = self.args.sources
        expander = FolderExpander()
        expander.suffixes_whitelist = self.__loader_classes.keys()
        yield from expander.expand(*s)

    def run(self):
        env.info(f'解析的参数：', self.args)

        if self.args.show_man:
            self.show_man()
            return

        if not self.args.sources:
            raise NoSourceError()

        if self.args.bypass_formatter:
            env.print('[red]旁通格式化器[/red] ...')

        with env.console.status('开始执行任务') as status:
            for s in self.sources():
                source = Path(s)
                status.update(f'{source.name} ...')
                self.do_job(source)


def run():
    with SubConvApp() as app:
        app.run()
