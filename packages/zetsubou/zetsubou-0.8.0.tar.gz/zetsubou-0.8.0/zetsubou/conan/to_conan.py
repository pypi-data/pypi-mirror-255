from copy import copy
from zetsubou.commands.base_command import CommandContext
from typing import Set, Tuple, List
from zetsubou.project.model.configuration import Configuration
from zetsubou.project.model.configuration_enums import EBaseConfiguration
from zetsubou.project.model.platform_enums import EArch, ESystem
from zetsubou.project.model.platform import Platform
from zetsubou.project.model.runtime_library import ERuntimeLibrary
from zetsubou.project.model.toolchain_profile import Windows_ToolchainProfile
from zetsubou.project.model.toolchain import ECompilerFamily, ECppStandard, Toolchain
from zetsubou.utils.common import Version


def platform_to_conan(context: CommandContext, plat : Platform) -> List[str]:
    return [
        '-s', f'os={plat.host_system.name}'
    ]


def msvc_version_to_conan(msvc_ver:Version) -> Tuple[str, str]:
    version = str(msvc_ver.major)
    version += str(msvc_ver.minor)[0]
    return (version, str(msvc_ver.minor)[1:])


def compiler_family_to_conan(family : ECompilerFamily):
    return {
        ECompilerFamily.MSVC.name  : 'msvc',
        ECompilerFamily.CLANG.name : 'clang',
        ECompilerFamily.GCC.name   : 'gcc'
    }.get(family.name)


def toolchain_to_conan(context: CommandContext, toolchain: Toolchain) -> List[str]:
    if toolchain is not None:

        arch = {
            EArch.x86.name : 'x86',
            EArch.x64.name : 'x86_64'
        }.get(toolchain.definition.arch)

        compiler = compiler_family_to_conan(toolchain.definition.CompilerFamily)

        result = [
            '-s', f'arch={arch}',
            '-s', f'compiler={compiler}',
        ]

        # TODO FIXME Conan should know about these, but there is no way to pass them via CLI anymore in 2.0 :(
        # for path in toolchain.definition.PathEnv:
        #     result.extend([
        #         '-e', f'PATH=[{path}]'
        #     ])

        result.extend(cppstd_to_conan(toolchain.profile.cppstd))

        if context.host_system == ESystem.Windows and toolchain.toolset is not None:
            if toolchain.definition.CompilerFamily == ECompilerFamily.CLANG:
                result.extend([
                    '-s', f'compiler.runtime_version={toolchain.toolset}'
                ])

        if toolchain.definition.CompilerFamily == ECompilerFamily.MSVC:
            version = msvc_version_to_conan(toolchain.definition.version)
            result.extend([
                '-s', f'compiler.version={version[0]}',
                '-s', f'compiler.update={version[1]}'
            ])
        else:
            # Remove path, conan is interested only in Major.Minor at best
            ver_no_path = copy(toolchain.definition.version)
            ver_no_path.path = 0

            result.extend([
                '-s', f'compiler.version={ver_no_path}'
            ])

        return result

    return []


def config_base_to_conan(context: CommandContext, config: Configuration) -> List[str]:
    if config is not None:

        build_type = {
            EBaseConfiguration.DEBUG : 'Debug',
            EBaseConfiguration.RELEASE : 'Release',
            EBaseConfiguration.RELEASE_WITH_DEBUG_INFO : 'RelWithDebInfo'
        }.get(config.base_configuration)

        result = [
            '-s', f'build_type={build_type}',
        ]

        return result

    return []


def cppstd_to_conan(cppstd:ECppStandard):
    cpp = {
        ECppStandard.cpp11  : '11',
        ECppStandard.cpp14  : '14',
        ECppStandard.cpp17  : '17',
        ECppStandard.cpp20  : '20',
        ECppStandard.cpp23  : '23',
        ECppStandard.latest : '23',
    }.get(cppstd)
    return [
        '-s', f"compiler.cppstd={cpp}"
    ]


def runtime_to_conan(config:Configuration, toolchain:Toolchain):
    if not isinstance(toolchain.profile, Windows_ToolchainProfile):
        return []

    runtime = {
        ERuntimeLibrary.dynamic : 'dynamic',
        ERuntimeLibrary.static : 'static'
    }.get(toolchain.profile.runtime)

    runtime_type = 'Debug' if config.base_configuration == EBaseConfiguration.DEBUG else 'Release'

    return [
        '-s', f'compiler.runtime={runtime}',
        '-s', f'compiler.runtime_type={runtime_type}'
    ]


def toolsets_from_settings(conan_settings : dict, compiler_family : ECompilerFamily) -> Set[str]:
    conan_compiler = compiler_family_to_conan(compiler_family)
    if compiler_family == ECompilerFamily.CLANG:
        try:
            return set(conan_settings['compiler'][conan_compiler]['runtime_version']) if conan_settings is not None else None
        except KeyError:
            return None
    else:
        return None
