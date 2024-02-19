from dataclasses import dataclass
from typing import Optional
from fs.base import FS
from zetsubou.project.model.platform_enums import ESystem, EArch
from zetsubou.project.model.virtual_environment import VirtualEnvironment


@dataclass
class BaseContext:
    host_system: ESystem = 0
    host_arch: EArch = 0
    fs_root: str = ''
    fs_venv: Optional[VirtualEnvironment] = None
    project_fs: FS = ''
    project_file: str = ''
