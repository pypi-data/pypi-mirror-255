from pathlib import Path
from .transcoder import make_target
from .env import env


def quote(filename) -> str:
    filename = str(filename)
    if filename.startswith('"') and filename.endswith('"'):
        return filename
    return '"' + filename + '"'


class ScriptWriter:
    def __init__(self, target, profile=None):
        self.target = Path(target).absolute()
        self.output = None
        self.planned_folders = set()
        self.ffmpeg = 'ffmpeg'
        self.profile = profile if profile else env.profile

    def __enter__(self):
        self.output = open(self.target, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.output.flush()
        self.output.close()
        return False

    def global_options(self):
        for k, v in self.profile.general.options.items():
            yield '-' + k
            if v:
                yield v
        if self.profile.general.hardware_accelerate:
            yield '-hwaccel'
            yield self.profile.general.hardware_accelerate
        if self.profile.general.overwrite_existed:
            yield '-y'
        else:
            yield '-n'

    def input_options(self):
        for k, v in self.profile.input.options.items():
            yield '-' + k
            if v:
                yield v

    def output_options(self):
        for k, v in self.profile.output.options.items():
            yield '-' + k
            if v:
                yield v

    def write(self, source: Path | str):
        line = [self.ffmpeg]
        target = make_target(Path(source), self.profile)
        folder = Path(target).parent

        if not folder.exists() and folder not in self.planned_folders:
            self.output.write(f'mkdir -p {quote(folder.absolute())}\n')
            env.debug(f'写入新建文件夹{folder}的任务')
            self.planned_folders.add(folder)

        for i in self.global_options():
            line.append(i)

        for i in self.input_options():
            line.append(i)

        line.append('-i')
        line.append(quote(source.absolute()))

        for i in self.output_options():
            line.append(i)

        line.append(quote(target))
        cmd = " ".join(line)
        self.output.write(f'{cmd}\n')
        env.debug(f'写入命令{cmd}')
