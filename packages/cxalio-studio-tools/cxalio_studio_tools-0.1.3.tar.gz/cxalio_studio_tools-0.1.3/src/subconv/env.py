from rich.console import Console

from cx_core import AbstractEnv, AppLogger


class Env(AbstractEnv):
    def __init__(self):
        super(Env, self).__init__()
        self.console = Console()
        self._logger = AppLogger(console=self.console)


env = Env()
