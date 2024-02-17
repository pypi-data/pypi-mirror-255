from pathlib import Path
from .utils import normalize_path


class FolderExpander:
    def __init__(self, **kwargs):
        self.suffixes_blacklist = []
        self.suffixes_whitelist = []
        self.working_directory = '.'
        self.existed_only = True
        self.follow_symlinks = True
        self.accept_files = True
        self.accept_folders = True
        if kwargs is not None:
            self.__dict__.update(kwargs)

    def __make_absolute(self, path: Path):
        return normalize_path(path,self.working_directory)

    def __is_acceptable_file(self, path: Path):
        if not self.accept_files:
            return False
        if not path.is_file():
            return False
        if self.existed_only and not path.exists():
            return False
        suffix = path.suffix.lower()
        if self.suffixes_whitelist:
            return suffix in self.suffixes_whitelist
        return suffix not in self.suffixes_blacklist

    def __is_acceptable_folder(self, path: Path):
        if not self.accept_folders:
            return False
        return path.is_dir()

    def expand(self, *entries):
        for entry in entries:
            p = self.__make_absolute(entry)
            if self.__is_acceptable_file(p):
                yield p
            elif self.__is_acceptable_folder(p):
                for sub in p.iterdir():
                    yield from self.expand(p / sub)
