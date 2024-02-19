from typing import List, Optional
import os

from bentoudev.dataclass.yaml_loader import LineLoader

from zetsubou.project.model.virtual_environment import VirtualEnvironment
from zetsubou.utils.subprocess import call_process, call_process_venv
import zetsubou.utils.logger as logger


def check_conan_present():
    out, err = call_process(['conan', '--version'], capture=True, realtime=False)
    if err is not None:
        logger.CriticalError('Conan is missing, unable to proceed')
        return False

    prefix = 'Conan version'
    prefix_pos = out.find(prefix)
    version = out[prefix_pos + len(prefix):].strip()

    logger.Success(f"Conan {version} present")
    return True


def get_conan_settings():
    user_dir = os.path.expanduser('~')
    conan_settings_path = os.path.join(user_dir, '.conan/settings.yml')

    if os.path.exists(conan_settings_path):
        with open(conan_settings_path, encoding='utf-8') as conan_settings_file:
            loader = LineLoader(conan_settings_file.read())
            return loader.get_single_data()

    return None


def call_conan(args : List[str], cwd : str, venv : Optional[VirtualEnvironment] = None):
    verbose = logger.IsVisible(logger.ELogLevel.Verbose)

    out = None
    err = None

    if venv is not None:
        out, err = call_process_venv(['conan'] + args, venv, capture = not verbose, realtime = verbose, cwd = cwd)
    else:
        out, err = call_process(['conan'] + args, capture = not verbose, realtime = verbose, cwd = cwd)

    if err is not None:
        if not verbose:
            logger.CriticalError(f'Conan command failed: {" ".join(args)}')
            logger.Error(out)

        logger.CriticalError(f"Conan returned error '{err}'")
        return False
    return True
