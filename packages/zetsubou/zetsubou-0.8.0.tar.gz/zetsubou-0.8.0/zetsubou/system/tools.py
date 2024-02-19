import ctypes
import sys
from typing import List
from zetsubou.project.model.platform_enums import ESystem, EArch
from zetsubou.project.model.platform import Platform


def get_host_system() -> ESystem:
    if sys.platform == 'win32':
        return ESystem.Windows
    if sys.platform in [ 'linux', 'linux2' ]:
        return ESystem.Linux
    raise EnvironmentError(f'Sorry, \"{sys.platform}\" is not currently supported!')


def get_host_arch() -> EArch:
    # More architectures might be needed here
    if is_64_bit():
        return EArch.x64
    return EArch.x86


def filter_platforms_by_host(host_system: ESystem, host_arch: EArch, platforms: List[Platform]) -> List[Platform]:
    results = []
    for plat in platforms:
        if plat.host_arch == host_arch and plat.host_system == host_system:
            results.append(plat)
    return results


def is_64_bit():
    return ctypes.sizeof(ctypes.c_void_p) == 8
