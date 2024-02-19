from enum import Enum, auto


# class ERuntimeLibrary(Enum):
#     DYNAMIC_DEBUG   = 0,
#     DYNAMIC_RELEASE = 1,
#     STATIC_DEBUG    = 2,
#     STATIC_RELEASE  = 3


class ERuntimeLibrary(Enum):
    dynamic = auto()
    static = auto()
