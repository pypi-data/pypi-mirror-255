import signal
import asyncio

from rich.progress import Progress, SpinnerColumn, MofNCompleteColumn

from cx_core import AppLogger, AbstractEnv, LogLevel, DataPackage


class Env(AbstractEnv):
    def __init__(self):
        super(Env,self).__init__()
        self._progress = Progress(
            SpinnerColumn(),
            # MofNCompleteColumn(),
            *Progress.get_default_columns(),
            # expand=True,
            transient=True)

        self._logger = AppLogger(console=self._progress.console)
        self._logger.level = LogLevel.WARNING

        self.args = None
        self.profile = DataPackage()

        self.current_ffmpeg = None
        self.wanna_quit = False

    def start(self):
        self._progress.start()
        self.info('Started ...')

    def stop(self):
        self._progress.stop()
        self.info('Bye~')

    @property
    def progress(self):
        return self._progress

    @property
    def console(self):
        return self._progress.console


env = Env()


def signal_handler(sig, frame):
    if sig != signal.SIGINT:
        return
    env.info('接收到 SIGINT')
    env.print("收到终止信号，准备退出...")
    env.wanna_quit = True
    if env.current_ffmpeg:
        env.current_ffmpeg.terminate()


signal.signal(signal.SIGINT, signal_handler)
