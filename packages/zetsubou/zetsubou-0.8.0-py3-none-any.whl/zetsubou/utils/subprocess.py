from subprocess import Popen as process_open
from subprocess import PIPE, STDOUT
from sys import stdout as sys_stdout
from typing import List, Callable, Optional

from zetsubou.project.model.virtual_environment import VirtualEnvironment
from zetsubou.utils.common import fix_path_os
from zetsubou.utils.error_codes import EErrorCode


class EnterVenv():
    venv_obj : Optional[VirtualEnvironment] = None

    def __init__(self, venv_obj : VirtualEnvironment):
        self.venv_obj = venv_obj

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def call_process(self, args : List[str], realtime : bool = False, capture : bool = True, on_error : Callable[[int], EErrorCode] = None, cwd: str = '.'):
        return call_process_venv(args, self.venv_obj, realtime, capture, on_error, cwd)


def call_process_venv(args : List[str], venv : VirtualEnvironment, realtime : bool = False, capture : bool = True, on_error : Callable[[int], EErrorCode] = None, cwd: str = '.'):
    return call_process([ fix_path_os(venv.activate), '&&' ] + args, realtime, capture, on_error, cwd)


def call_process(args : List[str], realtime : bool = False, capture : bool = True, on_error : Callable[[int], EErrorCode] = None, cwd: str = '.'):
    str_buff : List[str] = []
    err = None

    with process_open(args, encoding=sys_stdout.encoding, shell=True, stdout=PIPE, stderr=STDOUT, bufsize=1,
                universal_newlines=True, cwd=cwd, errors='ignore') as proc:

        while proc.stdout.readable():
            line = proc.stdout.readline()
            if capture:
                str_buff.append(line)
            if realtime:
                sys_stdout.write(line)

            if line == '' and proc.poll() is not None:
                break

        if proc.returncode != 0:
            if on_error is not None:
                err = on_error(proc.returncode)
            else:
                err = proc.returncode

        return (''.join(str_buff), err)
