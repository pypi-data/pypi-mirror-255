from typing import Optional
from zetsubou.project.model.platform_enums import EArch
from zetsubou.project.model.runtime_library import ERuntimeLibrary
from zetsubou.utils.error import ProjectError

def arch_to_msvc_platform(arch : EArch):
    lookup = {
        EArch.x64 : 'x64',
        EArch.x86 : 'Win32'
    }

    if arch not in lookup:
        raise ProjectError(f"Arch '{arch}' is not supported for MSVC!")

    return lookup.get(arch)

# def runtime_from_msvc_legacy(runtime:str) -> Optional[ERuntimeLibrary]:
#     return {
#         'MD' : ERuntimeLibrary.DYNAMIC_RELEASE,
#         'MDd' : ERuntimeLibrary.DYNAMIC_DEBUG,
#         'MT' : ERuntimeLibrary.STATIC_RELEASE,
#         'MTd' : ERuntimeLibrary.STATIC_DEBUG
#     }.get(runtime, None)
