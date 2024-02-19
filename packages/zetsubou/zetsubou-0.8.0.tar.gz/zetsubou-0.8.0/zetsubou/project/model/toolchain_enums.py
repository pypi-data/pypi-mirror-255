from enum import Enum, auto


class ECompilerFamily(Enum):
    MSVC     = auto()
    CLANG    = auto()
    CLANG_CL = auto()
    GCC      = auto()
    CUSTOM   = auto()


class ELibrarianFamily(Enum):
    MSVC = auto()
    LLVM = auto()
    GCC  = auto()


class ELinkerFamily(Enum):
    LINK     = auto() # MSVC
    LLD_LINK = auto()
    LD_LLD   = auto()
    LD       = auto() # GCC


class ECppStandard(Enum):
    cpp11 = auto()
    cpp14 = auto()
    cpp17 = auto()
    cpp20 = auto()
    cpp23 = auto()
    latest = auto()

    @staticmethod
    def default():
        return ECppStandard.cpp20
