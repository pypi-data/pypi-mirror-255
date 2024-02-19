# pyright: reportMissingImports=false
# pylint: disable=import-error, bare-except
from typing import Optional, List, Union
from dataclasses import dataclass, field

# This file can be imported from conan generator
# So it needs to support importing via absolute and relative packages
try:
    from zetsubou.project.model.configuration_enums import EBaseConfiguration
    from zetsubou.project.model.platform_enums import EArch, EVersionSelector
    from zetsubou.project.model.runtime_library import ERuntimeLibrary
    from zetsubou.project.model.toolchain_enums import ECompilerFamily, ECppStandard
except:
    pass


try:
    from configuration_enums import EBaseConfiguration
    from platform_enums import EArch, EVersionSelector
    from runtime_library import ERuntimeLibrary
    from toolchain_enums import ECompilerFamily, ECppStandard
except:
    pass


@dataclass
class IToolchainProfile:
    target_arch: Optional[EArch] = None
    compiler_family: Optional[ECompilerFamily] = None
    compiler_version: Optional[Union[EVersionSelector, str]] = None
    cppstd: Optional[ECppStandard] = None


@dataclass
class Windows_ToolchainProfile(IToolchainProfile):
    toolset: Optional[Union[EVersionSelector, str]] = None
    runtime: Optional[ERuntimeLibrary] = None


@dataclass
class Linux_ToolchainProfile(IToolchainProfile):
    libcxx: Optional[str] = None


@dataclass
class Profile:
    build_type: Optional[EBaseConfiguration] = None
    toolchains: List[Union[IToolchainProfile, Windows_ToolchainProfile, Linux_ToolchainProfile]] = field(default_factory=list)
