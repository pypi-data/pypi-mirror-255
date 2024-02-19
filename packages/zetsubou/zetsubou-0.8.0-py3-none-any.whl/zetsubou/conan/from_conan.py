# pyright: reportMissingImports=false
# pylint: disable=import-error, bare-except

# This file can be imported from conan generator
# So it needs to support importing via absolute and relative packages
import configparser
from typing import Optional
from conan import ConanFile

try:
    from zetsubou.project.model.configuration_enums import EBaseConfiguration
    from zetsubou.project.model.runtime_library import ERuntimeLibrary
    from zetsubou.project.model.toolchain_enums import ECompilerFamily, ECppStandard
    from zetsubou.project.model.platform_enums import EArch, ESystem, EVersionSelector
    from zetsubou.project.model.toolchain_profile import Profile, IToolchainProfile, Windows_ToolchainProfile, Linux_ToolchainProfile
    from zetsubou.utils.yaml_simple_writer import to_yaml
except:
    pass


try:
    from configuration_enums import EBaseConfiguration
    from runtime_library import ERuntimeLibrary
    from toolchain_enums import ECompilerFamily, ECppStandard
    from platform_enums import EArch, ESystem, EVersionSelector
    from toolchain_profile import Profile, IToolchainProfile, Windows_ToolchainProfile, Linux_ToolchainProfile
    from yaml_simple_writer import to_yaml
except:
    pass


defined = lambda o: o is not None


def os_from_conan(system:str) -> Optional[ESystem]:
    return {
        'Windows' : ESystem.Windows,
        'Linux' : ESystem.Linux
    }.get(system, None)


def arch_from_conan(arch:str) -> Optional[EArch]:
    return {
        'x86' : EArch.x86,
        'x86_64' : EArch.x64
    }.get(arch, None)


def compiler_family_from_conan(compiler:str) -> Optional[ECompilerFamily]:
    return {
        'Visual Studio' : ECompilerFamily.MSVC,
        'msvc' : ECompilerFamily.MSVC,
        'gcc' : ECompilerFamily.GCC,
        'clang' : ECompilerFamily.CLANG,
    }.get(compiler, None)


def runtime_from_conan(runtime:str):
    return {
        'dynamic' : ERuntimeLibrary.dynamic,
        'static' : ERuntimeLibrary.static
    }.get(runtime, None)


def cppstd_from_conan(cppstd:str) -> Optional[ECppStandard]:
    return {
        '11' : ECppStandard.cpp11,
        '14' : ECppStandard.cpp14,
        '17' : ECppStandard.cpp17,
        '20' : ECppStandard.cpp20,
        '23' : ECppStandard.cpp23,
    }.get(cppstd, None)


def build_type_from_conan(build_type:str) -> Optional[EBaseConfiguration]:
    return {
        'Debug' : EBaseConfiguration.DEBUG,
        'Release' : EBaseConfiguration.RELEASE,
        'RelWithDebInfo' : EBaseConfiguration.RELEASE_WITH_DEBUG_INFO
    }.get(build_type, None)


def runtime_library_from_conan(conanfile:ConanFile, build_type:EBaseConfiguration) -> ERuntimeLibrary:
    # always present
    runtime = conanfile.settings.get_safe('compiler.runtime')
    if runtime is None:
        conanfile.output.error('Runtime is not set!')
        return None

    # only in new compilers
    runtime_type = conanfile.settings.get_safe('compiler.runtime_type')

    if runtime_type is not None:
        if runtime_type == 'Release' and build_type not in [EBaseConfiguration.RELEASE, EBaseConfiguration.RELEASE_WITH_DEBUG_INFO]:
            conanfile.output.error('Runtime type doesnt match build type!')
            return None
        elif runtime_type == 'Debug' and build_type != EBaseConfiguration.DEBUG:
            conanfile.output.error('Runtime type doesnt match build type!')
            return None

        # in new compilers only two values are supported, debug flag is managed by build type
        return {
            'dynamic' : ERuntimeLibrary.dynamic,
            'static'  : ERuntimeLibrary.static
        }.get(runtime, None)

    else:
        deduced_runtime, deduced_type = {
            'MD'  : (ERuntimeLibrary.dynamic, EBaseConfiguration.RELEASE),
            'MDd' : (ERuntimeLibrary.dynamic, EBaseConfiguration.DEBUG),
            'MT'  : (ERuntimeLibrary.static, EBaseConfiguration.RELEASE),
            'MTd' : (ERuntimeLibrary.static, EBaseConfiguration.DEBUG),
        }.get(runtime, (None, None))

        if deduced_runtime is None or deduced_type is None:
            conanfile.output.error('Invalid value for runtime!')
            return None

        if deduced_type == EBaseConfiguration.RELEASE and build_type in [EBaseConfiguration.RELEASE, EBaseConfiguration.RELEASE_WITH_DEBUG_INFO]:
            return deduced_runtime

        if deduced_type == EBaseConfiguration.DEBUG and build_type == EBaseConfiguration.DEBUG:
            return deduced_type

    conanfile.output.error('Unable to determine runtime library!')
    return None


def export_profile(conanfile:ConanFile, platform_filename:str) -> bool:
    build_type = build_type_from_conan(conanfile.settings.get_safe('build_type'))
    if build_type is None:
        conanfile.output.error('Unable to setup Profile')
        return None

    compiler = toolchain_from_settings(conanfile, build_type)
    if compiler is None:
        conanfile.output.error('Unable to setup Toolchain')
        return False

    profile = Profile(build_type=build_type, toolchains=[ compiler ])

    with open(platform_filename, 'w') as out_file:
        out_file.write(to_yaml(profile))

    return True


def toolchain_from_settings(conanfile:ConanFile, build_type:EBaseConfiguration) -> Optional[IToolchainProfile]:
    arch_host = None
    arch_target = None
    arch = conanfile.settings.get_safe('arch')
    if arch is None:
        arch_host = conanfile.settings.get_safe('arch_build')
        arch_target = conanfile.settings.get_safe('arch_target')
    else:
        arch_target = arch
        arch_host = arch

    arch_host = arch_from_conan(arch_host)
    arch_target = arch_from_conan(arch_target)
    os_host = os_from_conan(conanfile.settings.get_safe('os'))

    if not defined(os_host) or not (defined(arch_target) and defined(arch_host)):
        return None

    compiler_family = compiler_family_from_conan(conanfile.settings.get_safe('compiler'))
    if compiler_family is None:
        print('Unable to discover compiler family')
        return None

    compiler_version = conanfile.settings.get_safe('compiler.version')
    if compiler_version is None:
        compiler_version = EVersionSelector.latest

    cppstd = cppstd_from_conan(conanfile.settings.get_safe('compiler.cppstd'))
    if cppstd is None:
        cppstd = ECppStandard.default()

    # if compiler_family in (ECompilerFamily.MSVC, ECompilerFamily.CLANG, ECompilerFamily.CLANG_CL):
    if os_host == ESystem.Windows:
        compiler_toolset = conanfile.settings.get_safe('compiler.toolset')
        if compiler_toolset is None:
            compiler_toolset = EVersionSelector.latest

        runtime_library = runtime_library_from_conan(conanfile, build_type)
        if runtime_library is None:
            return None

        return Windows_ToolchainProfile(
            target_arch=arch_target,
            compiler_family=compiler_family,
            compiler_version=compiler_version,
            cppstd=cppstd,
            toolset=compiler_toolset,
            runtime=runtime_library
        )
    else:
        compiler_libcxx = conanfile.settings.get_safe('compiler.libcxx')
        if compiler_libcxx is None:
            print('Unable to discover compiler libcxx')
            return None

        return Linux_ToolchainProfile(
            target_arch=arch_target,
            compiler_family=compiler_family,
            compiler_version=compiler_version,
            cppstd=cppstd,
            libcxx=compiler_libcxx
        )


def toolchain_from_profile(conan_profile:str) -> Optional[IToolchainProfile]:
    config = configparser.ConfigParser()

    with open(conan_profile, 'r') as file:
        config.read_file(file)

        if not config.has_section('settings'):
            return None

        settings = config['settings']

        arch = arch_from_conan(settings.get('arch'))
        if arch is None:
            return None

        system = os_from_conan(settings.get('os'))
        if system is None:
            return None

        compiler_family = compiler_family_from_conan(settings.get('compiler'))
        if compiler_family is None:
            return None

        compiler_version = settings.get('compiler.version')
        if compiler_version is None:
            compiler_version = EVersionSelector.latest

        cppstd = cppstd_from_conan(settings.get('compiler.cppstd'))
        if cppstd is None:
            cppstd = ECppStandard.default()

        if system == ESystem.Windows:
            compiler_runtime = runtime_from_conan(settings.get('compiler.runtime'))
            if compiler_runtime is None:
                return None

            # Used to be compiler.toolset in Visual Studio and Clang
            # Now only Clang defines it (msvc probably guesses latest from version)
            compiler_toolset = settings.get('compiler.runtime_version')
            if compiler_toolset is None:
                compiler_toolset = EVersionSelector.latest

            return Windows_ToolchainProfile(
                target_arch=arch,
                compiler_family=compiler_family,
                compiler_version=compiler_version,
                cppstd=cppstd,
                toolset=compiler_toolset,
                runtime=compiler_runtime
            )

        elif system == ESystem.Linux:
            compiler_libcxx = settings.get('compiler.libcxx')
            if compiler_libcxx is None:
                return None

            return Linux_ToolchainProfile(
                target_arch=arch,
                compiler_family=compiler_family,
                compiler_version=compiler_version,
                cppstd=cppstd,
                libcxx=compiler_libcxx
            )

        return None
