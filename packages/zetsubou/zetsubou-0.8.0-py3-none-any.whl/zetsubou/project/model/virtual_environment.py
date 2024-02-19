import os
import venv
from dataclasses import dataclass
from typing import List, Optional
from fs.base import FS

from zetsubou.project.model.project_template import Project
from zetsubou.utils.common import fix_path
from zetsubou.utils.error import ProjectError
import zetsubou.utils.logger as logger


# Class which contains paths to scripts which activate and deactivate virtual environment
# We cannot assume scripts have a particular name due to conan changing convention mid development
@dataclass
class VirtualEnvironment:
    activate: str
    deactivate: str

    @property
    def path(self):
        return os.path.dirname(self.activate)


# Generates new, clean virtual environment in provided FS
def generate_empty_environment(project_fs: FS):
    env_builder = venv.EnvBuilder()
    venv_fs = project_fs.geturl('build/venv', purpose='fs')
    venv_fs = venv_fs.split('osfs://')[1]
    env_builder.create(venv_fs)
    logger.Info('Created new virtual environment')


# Returns path to file which activates virtual environment
# Since conan is quirky, deactivation file might not exists before activation is first called
# Hence we need to assume path here
def resolve_venv(project_fs : FS, proj : Project, proj_path : str) -> Optional[VirtualEnvironment]:
    if proj.config.venv == '':

        def find_script(patterns : List[str]):
            for path in project_fs.walk.files(filter=patterns):
                env_dir = path
                if env_dir.startswith('/'):
                    env_dir = env_dir[1:]
                return env_dir
            return ''

        activate = fix_path(find_script(['activate.*', 'conanbuild.*', 'conanbuildenv*']))
        deactivate = fix_path(find_script(['deactivate.*', 'deactivate_conanbuild.*', 'deactivate_conanbuildenv*']))

        # Conan activation script generates deactivation on first call
        if activate != '' and deactivate == '':
            deactivate = activate.replace('conanbuildenv', 'deactivate_conanbuildenv')

        if activate == '' or deactivate == '':
            proj_yml_path = proj.get_loaded_from_file()
            logger.CriticalError('Virtual environment not found! \n'
                f" Please, either set path to config.venv in {proj_yml_path}, run 'zetsubou install' command, or place 'activate' and 'deactivate' scripts in one of the project subdirectories.")
            return None

        return VirtualEnvironment(activate=activate, deactivate=deactivate)

    else:
        venv = os.path.abspath(os.path.join(proj_path, proj.config.venv))

        def find_script_os(search_root : str, prefixes : List[str]) -> Optional[str]:
            for _, _, files in os.walk(search_root):
                for file in files:
                    if any(filter(lambda p, f=file : f.find(p) != -1, prefixes)):
                        return file
            return ''

        if os.path.exists(venv) and os.path.isdir(venv):
            activate = fix_path(find_script_os(venv, ['activate.', 'conanbuild.', 'conanbuildenv']))
            deactivate = fix_path(find_script_os(venv, ['deactivate.', 'conanbuild_deactivate.', 'deactivate_conanbuildenv']))

            # Conan activation script generates deactivation on first call
            if activate != '' and deactivate == '':
                deactivate = activate.replace('conanbuildenv', 'deactivate_conanbuildenv')

            if activate == '' or deactivate == '':
                proj_yml_path = proj.get_loaded_from_file()
                logger.CriticalError('Virtual environment not found! \n'
                    f" Path '{proj.config.venv}' doesn't contain 'activate' and 'deactivate' scripts! Run 'zetsubou install' command or create them manually.")
                return None

            return VirtualEnvironment(
                activate=os.path.join(proj.config.venv, activate),
                deactivate=os.path.join(proj.config.venv, deactivate))

        else:
            raise ProjectError(proj.config.format_field_message("venv", "error",
                f"Virtual environment not found! Path '{proj.config.venv}' doesnt exist or is not a directory!",
                logger.GetErrorFormat())
            )
