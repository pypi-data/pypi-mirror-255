import itertools
from itertools import groupby
from pathlib import Path

from cx_core.folder_expander import FolderExpander
from .env import env
from .source_adapter import adapters


class Planner:
    _DEFAULT_SUFFIXES = ("mov mkv mp4 flv 3gp 3gpp rmvb mp3 aac"
                         " mxf mxf_op1a vob wmv wma srt ass aas ttml ogg oga ogv m4a"
                         " m4v 3g2 mpeg mpg ts lrc h264 flac ast asf gif")

    def __init__(self):
        self._loaded_file = set()
        self.plans = []
        env.debug('Planner 初始化')

    def __len__(self):
        return len(self.plans)

    def __iter__(self):
        return self.plans.__iter__()

    def load_source(self, filename):
        source = Path(filename)
        if not source.is_absolute():
            source = env.profile.general.working_folder / source
        suffix = source.suffix.lower().strip('.')
        env.debug(f'文件 "{source}" 的扩展名为 "{suffix}"')
        if suffix in adapters:
            env.debug(f'已识别 "{source}" 为列表文件')
            try:
                with adapters[suffix](source) as adp:
                    for item in adp.items():
                        env.debug(f'发现文件路径 "{item}"')
                        self.plans.append(item)
            except FileNotFoundError:
                env.error(f'文件 {source} 不存在，无法读取')
            finally:
                self._loaded_file.add(source)
        else:
            self.plans.append(source)
            self._loaded_file.add(source)
            env.debug(f'文件 "{source}" 无法识别为列表文件，将直接添加进入计划')

    def load_sources(self, filenames):
        task = env.progress.add_task(description='读取来源文件...')
        for f in env.progress.track(filenames, task_id=task):
            self.load_source(f)
        env.progress.remove_task(task)

    def arrange(self, profile=None):
        if not profile:
            profile = env.profile

        env.info('开始整理计划列表')

        env.debug('构建 Expander ...')
        expander = FolderExpander()
        expander.working_directory = profile.general.work_folder

        env.debug('构建扩展名白名单')
        _basic_suffixes = {str(x).strip('.') for x in
                           itertools.chain(Planner._DEFAULT_SUFFIXES.split(), profile.input.suffix_includes)}
        _blacklist = {str(x).strip('.') for x in profile.input.suffix_excludes}
        w_list = _basic_suffixes - _blacklist
        env.debug('生成扩展名白名单 [cyan]{" ".join(w_list)}[/cyan]')
        expander.suffixes_whitelist = ['.' + x for x in w_list]

        env.info('开始展开文件夹')
        new_files = [Path(x) for x in expander.expand(*self.plans)]
        env.info('正在根据路径进行排序')
        new_files = sorted(new_files, key=lambda a: a.absolute())

        env.info('开始逐个检查文件')
        arranged_files = []
        task = env.progress.add_task(description='检查文件列表...')
        for k, v in env.progress.track(groupby(new_files), task_id=task):
            kk = Path(k)
            if not kk.exists():
                env.warning(f'文件 "{kk}" 不存在，将从任务列表中去除')
                continue
            arranged_files.append(kk)
            env.debug(f'重新添加 "{kk}"')
            count = len(list(v))
            if count > 1:
                env.debug(f'发现 {count} 个重复的 "{k}" ，已经去除')
        env.progress.remove_task(task)
        self.plans = arranged_files
        env.info('计划列表自动整理完毕')
