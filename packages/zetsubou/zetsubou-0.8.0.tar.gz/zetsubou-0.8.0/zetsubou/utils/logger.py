import sys
import traceback
from enum import Enum
from colorama import Fore, Style, Back
from colorama import init as colorama_init
from zetsubou.utils.error_codes import EErrorCode
from bentoudev.dataclass.base import EErrorFormat


class ELogLevel(Enum):
    Verbose = 0
    Info = 1
    Warning = 2
    Error = 3
    Critical = 4
    Silent = 5


class scope_level:
    level: ELogLevel
    prev: ELogLevel

    def __init__(self, level: ELogLevel):
        self.level = level

    def __enter__(self):
        self.prev = LoggerStorage.log_level
        SetLogLevel(self.level)

    def __exit__(self, exc_type, exc_val, exc_tb):
        SetLogLevel(self.prev)


class LoggerStorage:
    log_level : ELogLevel = ELogLevel.Info
    ide : bool = False


def Initialize():
    colorama_init()


def SetLogLevel(log_level : ELogLevel):
    LoggerStorage.log_level = log_level


def SetIde(mode:bool):
    LoggerStorage.ide = mode


def IsVisible(level : ELogLevel):
    if level.value < LoggerStorage.log_level.value:
        return False
    return True


def IsIde():
    return LoggerStorage.ide


def GetErrorFormat() -> EErrorFormat:
    return EErrorFormat.MSVC if IsIde() else EErrorFormat.Pretty


def _prefix():
    if LoggerStorage.ide:
        return ''
    else:
        return '\r'


def ReturnCode(code: EErrorCode):
    if code == 0x0:
        Success('Returned code 0')
    elif IsVisible(ELogLevel.Critical):
        print(f'{_prefix()}{Fore.RED}{Back.WHITE} Returned error code {code.value} - {code.name} {Style.RESET_ALL}')


def CriticalError(err):
    if IsVisible(ELogLevel.Critical):
        print(_prefix())
        print(f'{_prefix()}{Fore.WHITE}{Back.RED} {err} {Style.RESET_ALL}')


def Exception(ex):
    if IsVisible(ELogLevel.Error):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        msg = 'Exception occured, '.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        Error(msg)


def Error(err):
    if IsVisible(ELogLevel.Error):
        print(_prefix())
        print(f'{_prefix()}{Fore.RED}{err}{Style.RESET_ALL}')


def Warning(warn):
    if IsVisible(ELogLevel.Warning):
        print(f'{_prefix()} - {Fore.YELLOW}{warn}{Style.RESET_ALL}')


def Info(inf):
    if IsVisible(ELogLevel.Info):
        print(f'{_prefix()} - {inf}')


def Success(suc):
    if IsVisible(ELogLevel.Info):
        print(f'{_prefix()} - [{Fore.GREEN}ok{Style.RESET_ALL}] {suc}')


def Loading(type: str, name: str):
    if IsVisible(ELogLevel.Info):
        print(f'{_prefix()} - Loading [{Fore.LIGHTBLUE_EX}{type}{Style.RESET_ALL}] \'{name}\'')


def Command(name: str):
    if IsVisible(ELogLevel.Info):
        print(f'{_prefix()}\n - Command [{Fore.CYAN}{name}{Style.RESET_ALL}]')


def Verbose(verb):
    if IsVisible(ELogLevel.Verbose):
        print(f'{_prefix()} - {verb}')
