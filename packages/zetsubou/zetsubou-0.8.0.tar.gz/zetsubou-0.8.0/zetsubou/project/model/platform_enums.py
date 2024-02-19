from enum import Enum, auto


class EArch(Enum):
    x64 = auto()
    x86 = auto()


class ESystem(Enum):
    Windows = auto()
    Linux = auto()


class EVersionSelector(Enum):
    # all = auto()
    latest = auto()
