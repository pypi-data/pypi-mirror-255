from enum import Enum, auto

# For compatibility purposes, custom configurations must fallback to one of the default ones, to communicate with VS and Conan
class EBaseConfiguration(Enum):
    DEBUG = auto()
    RELEASE = auto()
    RELEASE_WITH_DEBUG_INFO = auto()
