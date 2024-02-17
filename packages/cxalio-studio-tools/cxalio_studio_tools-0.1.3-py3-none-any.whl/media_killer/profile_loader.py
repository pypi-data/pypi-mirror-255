import tomllib
from collections.abc import Iterable
from pathlib import Path

from cx_core import DataPackage
from cx_core.utils import normalize_path
from .env import env


class ProfileNoFoundError(FileNotFoundError):
    def __init__(self, target=None):
        super(ProfileNoFoundError, self).__init__()
        self._tgt = target

    def __str__(self):
        if self._tgt:
            return f'ffmpeg 配置文件 "{self._tgt}" 未找到，程序无法执行'
        return '未指定配置文件，程序无法运行'


class ProfileLoader:
    def __init__(self):
        self.task_id = None

    def __enter__(self):
        self.task_id = env.progress.add_task(description='初始化配置信息', start=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        env.progress.remove_task(self.task_id)
        self.task_id = None

    @staticmethod
    def __make_sure_list(a=None):
        if not a:
            return []
        if isinstance(a, str):
            return a.split(' ')
        if isinstance(a, Iterable):
            return [str(x) for x in a]
        return [x for x in str(a).split(' ')]

    @staticmethod
    def __check_options(a=None):
        if not a:
            return {}
        if isinstance(a, str):
            return ProfileLoader.__arrange_options(a.split(' '))
        if isinstance(a, dict | DataPackage):
            return {**a}
        if isinstance(a, list):
            return ProfileLoader.__arrange_options(a)
        return ProfileLoader.__arrange_options(str(a).split(' '))

    @staticmethod
    def __arrange_options(a: list) -> dict:
        result = {}
        previous_key = None
        for x in a:
            word = str(x)
            if word.startswith('-'):
                if previous_key:
                    result[previous_key] = None
                    previous_key = None
                else:
                    previous_key = word[1:]
            else:
                if previous_key:
                    result[previous_key] = word
                    previous_key = None
                else:
                    env.debug(f'已忽略无法识别的参数{word}')
        if previous_key:
            result[previous_key] = None
        return result

    def __check_data_package(self, package):
        env.progress.update(self.task_id, description='解析配置文件数据', completed=1, total=2)
        env.info('检查配置数据...')

        result = DataPackage(**package)
        env.debug(f'配置文件：[cyan]{result.general.name}[/cyan]:[yellow]{result.general.description}[/yellow]')

        if not result.general.working_folder:
            env.debug('配置文件未指定工作目录')
            profile_folder = normalize_path('.' if not result.profile_path else result.profile_path.absolute().parent)
            result.general.working_folder = profile_folder
        env.debug(f'general.working_folder 已设置为 {result.general.working_folder}')

        env.info('开始格式化特殊设置')
        result.general.options = ProfileLoader.__check_options(result.general.options)
        result.input.options = ProfileLoader.__check_options(result.input.options)
        result.output.options = ProfileLoader.__check_options(result.output.options)
        result.input.files = ProfileLoader.__make_sure_list(result.input.files)
        result.input.suffix_includes = ProfileLoader.__make_sure_list(result.input.suffix_includes)
        result.input.suffix_excludes = ProfileLoader.__make_sure_list(result.input.suffix_excludes)

        env.debug('增加手动指定的源文件')
        result.input.files.extend(ProfileLoader.__make_sure_list(env.args.sources))

        if not result.output.folder:
            env.debug('未设置目标文件夹')
            result.output.folder = Path('.')
        result.output.folder = normalize_path(result.output.folder, result.general.working_folder)

        return result

    def load(self, filename):
        result = {}
        env.progress.start_task(self.task_id)
        env.progress.update(self.task_id, completed=0, total=2)
        task = env.progress.add_task(description=f'读取{filename}...')
        try:
            with env.progress.open(filename, 'rb', task_id=task) as fp:
                result.update(tomllib.load(fp))
            result['profile_path'] = Path(filename)
            return self.__check_data_package(result)
        except FileNotFoundError:
            raise ProfileNoFoundError(filename)
        finally:
            env.progress.remove_task(task)
