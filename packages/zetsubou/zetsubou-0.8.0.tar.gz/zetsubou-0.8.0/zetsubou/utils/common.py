from typing import List
from sys import platform
import os


class Version:
    major: int = 0
    minor: int = 0
    path: int = 0

    def __init__(self, ver_str:str):
        ver_parts = ver_str.split('.')

        num_sub_ver = len(ver_parts)
        if num_sub_ver == 0:
            return

        if num_sub_ver >= 1:
            self.major = int(ver_parts[0])

        if num_sub_ver >= 2:
            self.minor = int(ver_parts[1])

        if num_sub_ver >= 3:
            self.path = int(ver_parts[2])

    def __str__(self):
        if self.path != 0:
            return f"{self.major}.{self.minor}.{self.path}"
        if self.minor != 0:
            return f"{self.major}.{self.minor}"
        return str(self.major)

    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.path == other.path

    def __lt__(self, other):
        if self.major < other.major:
            return True
        elif self.major > other.major:
            return False

        if self.minor < other.minor:
            return True
        elif self.minor > other.minor:
            return False

        if self.path < other.path:
            return True
        elif self.path > other.path:
            return False

        return False


def foreach(lst, fn):
    if lst is None:
        return
    if len(lst) == 0:
        return
    for element in lst:
        fn(element)


def filter_none(lst):
    return filter(lambda i : i is not None, lst)


def is_in_enum(value, enum_class):
    if isinstance(value, enum_class):
        return True
    return value in enum_class.__members__


# Find more appropriate way to do this...
def fix_path(path : str):
    path = path.replace('\\\\', '/')
    path = path.replace('\\', '/')
    return path


def fix_path_win32(path : str):
    path = path.replace('/', '\\')
    return path


def fix_path_os(path : str):
    posix_path = fix_path(path)
    if platform == 'win32':
        return fix_path_win32(posix_path)
    return posix_path


def get_subdirs(dir: str):
    if not os.path.exists(dir):
        return []
    return [f.name for f in os.scandir(dir) if f.is_dir]


def get_files(dir: str):
    if not os.path.exists(dir):
        return []
    return [f.name for f in os.scandir(dir) if f.is_file]


def get_env_path() -> List[str]:
    env_path_str = os.getenv('PATH')
    return env_path_str.split(';')


# folder/subfolder/whatever/file.ext1.ext2 -> file
def filename_no_ext(path:str):
    base = os.path.basename(path)
    return base[:base.find('.')]


def null_or_empty(txt : str):
    return txt is None or txt == ''


def split(pred, collection):
    a = []
    b = []
    for element in collection:
        if pred(element):
            a.append(element)
        else:
            b.append(element)
    return a, b


# TODO replace with *args, this inline temporary array is unnecessary
def join_unique(lists : List[List[str]]):
    unique = list()
    for entry in lists:
        unique.extend(j for j in entry if j not in unique)
    return unique


def list_to_string(lists : List[str]):
    return f" {' '.join(lists)}"
