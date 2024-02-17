from pathlib import Path

from chardet.universaldetector import UniversalDetector

__char_detector = UniversalDetector()


def detect_encoding(filename):
    __char_detector.reset()
    try:
        with open(filename, 'rb') as fp:
            for line in fp.readlines():
                __char_detector.feed(line)
                if __char_detector.done:
                    break
            result = __char_detector.result
            return result['encoding']
    except FileNotFoundError:
        return 'utf-8'


def normalize_path(path: Path, anchor=Path('.')) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path.absolute()

    t = str(path)
    if t.startswith('~'):
        return Path(t.replace('~', str(Path.home()))).absolute()

    return anchor.absolute() / path


def quote_path(path, quote_char='"') -> str:
    path = str(path)
    return f'"{path}"' if ' ' in path else path
