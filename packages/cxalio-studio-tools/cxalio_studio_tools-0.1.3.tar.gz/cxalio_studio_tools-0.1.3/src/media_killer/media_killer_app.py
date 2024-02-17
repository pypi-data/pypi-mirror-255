import pkgutil
from argparse import ArgumentParser, ArgumentError
from pathlib import Path

from rich.columns import Columns
from rich.markdown import Markdown
from rich.panel import Panel
from rich_argparse import RichHelpFormatter

from cx_core import AbstractApp
from cx_core import DataPackage
from cx_core.app_logger import LogLevel
from cx_core.utils import normalize_path
from .env import env
from .planner import Planner
from .profile_loader import ProfileLoader, ProfileNoFoundError
from .script_writer import ScriptWriter
from .transcoder import Transcoder


class MediaKillerApp(AbstractApp):
    def __init__(self):
        super(MediaKillerApp,self).__init__()
        self.global_task = None
        self.app_name = 'media-killer'
        self.app_version = '0.1.2'
        parser = ArgumentParser(prog=self.app_name, formatter_class=RichHelpFormatter,
                                description='简单批量转码工具', epilog='Designed by xiii_1991')
        parser.add_argument('profile', help='指定配置文件路径', default=None, nargs='?')
        parser.add_argument('-g', '--generate-example-profile',
                            action="store_true", dest='generate_example',
                            help='生成范例文件')
        parser.add_argument('-a', '--add-source',
                            action='append', dest='sources', metavar='SOURCE_FILE',
                            help='增加来源文件')
        parser.add_argument('-s', '--make-script',
                            dest='script_output', metavar='SCRIPT_OUTPUT',
                            help='生成对应的脚本文件')
        parser.add_argument('-d', '--debug',
                            action='store_true', dest='debug', help='显示调试信息')
        parser.add_argument('--dry-run',
                            dest='dry_run', action='store_true', help='空转模式，不执行命令')
        parser.add_argument('--man', help='显示详细的说明',
                            dest='show_man', action='store_true')
        parser.add_argument('-v', '--version', action='version', version=self.app_version,
                            help='显示软件版本信息')
        self._parser = parser
        self.args = None

    @staticmethod
    def show_man():
        data = pkgutil.get_data('media_killer', 'help.md').decode('utf_8')
        env.console.print(Markdown(data))

    @staticmethod
    def copy_example_profile(tgt):
        tgt = normalize_path(tgt)
        data = pkgutil.get_data('media_killer', 'example_project.toml')
        try:
            with open(tgt, 'xb') as file:
                file.write(data)
            env.print(f'模板配置文件已保存到 {env.args.profile} ，[red]请勿直接加载运行！[/red]')
        except FileExistsError:
            env.error('文件 {0} 已存在，禁止覆盖文件'.format(tgt))

    def __enter__(self):
        env.start()

        _args = self._parser.parse_args()
        self.args = DataPackage(**vars(_args))

        env.debug('解析命令行参数：', self.args)
        env.log_level = LogLevel.DEBUG if self.args.debug else LogLevel.WARNING
        env.args = self.args

        self.global_task = env.progress.add_task(description='全局进度', start=False, visible=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        env.progress.stop_task(self.global_task)
        env.progress.remove_task(self.global_task)
        self.global_task = None

        result = False
        if exc_type is None:
            pass
        elif issubclass(exc_type, ProfileNoFoundError):
            env.critical(exc_val)
            result = True
        elif issubclass(exc_type, ArgumentError):
            env.error('参数输入有误:', exc_val)
            result = True

        env.stop()
        return result

    def run(self):
        if env.args.show_man:
            MediaKillerApp.show_man()
            return

        if not env.args.profile:
            raise ProfileNoFoundError

        if env.args.generate_example:
            env.debug('检测到 "--generate-example" 参数，拷贝配置文件模板')
            env.progress.update(task_id=self.global_task, description='正在输出配置文件', visible=True)
            self.copy_example_profile(env.args.profile)
            return

        with ProfileLoader() as profile_loader:
            datas = profile_loader.load(env.args.profile)
            env.profile = datas
        env.info('配置信息已初始化')

        if not env.profile.input.files:
            env.error('未指定任何来源信息，无事可做')
            return

        planner = Planner()
        env.progress.update(task_id=self.global_task, description='正在将来源信息加入计划', visible=True)
        planner.load_sources(env.profile.input.files)
        env.info('已发现 {0} 项来源'.format(len(planner)))

        env.progress.update(task_id=self.global_task, description='正在整理来源信息', visible=True)
        planner.arrange(env.profile)
        env.print(f'整理结束，已添加 {len(planner)} 项计划')
        if env.args.debug:
            col = Columns(
                (Panel(Path(x).name, style='yellow', border_style='green', safe_box=True,
                       title=f'#{i}', title_align='left')
                 for i, x in enumerate(planner)),
                expand=True, equal=False, column_first=True
            )
            env.debug(col)

        if env.args.script_output is not None:
            env.progress.update(task_id=self.global_task, description='输出脚本文件', visible=True)
            env.debug('检测到 "--script" 参数，进行脚本输出')
            output_file = normalize_path(env.args.script_output)
            with ScriptWriter(output_file, env.profile) as writer:
                for plan in env.progress.track(planner, description=env.args.script_output):
                    writer.write(plan)
            env.print('已输出脚本文件 “{0}”'.format(env.args.script_output))
            return

        env.progress.update(self.global_task, description='总体进度', visible=True, total=len(planner))
        env.progress.start_task(self.global_task)
        for plan in planner:
            if env.wanna_quit:
                env.print('用户申请终止运，取消未完成的任务')
                break
            if env.args.dry_run:
                env.print(plan)
            else:
                with Transcoder(plan, env.profile) as coder:
                    coder.run()
            env.progress.advance(self.global_task)
        env.print('任务执行结束')


def run():
    with MediaKillerApp() as media_killer:
        media_killer.run()
