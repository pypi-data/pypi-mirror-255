import winreg
import os, json
from typing import List, Optional, Any
from dataclasses import dataclass
from zetsubou.project.model.platform_enums import EArch

from zetsubou.project.model.toolchain import ECompilerFamily, ToolchainDefinition
from zetsubou.system.windows import vswhere
from zetsubou.utils import logger
from zetsubou.utils.common import Version, get_env_path, get_files, get_subdirs
from zetsubou.utils.subprocess import call_process


def is_current_host(host: str, host_arch: EArch) -> bool:
    # x64
    if host.endswith('64'):
        if host_arch == EArch.x64:
            return True
    # x86 (32-bit)
    else:
        if host_arch != EArch.x64:
            return True
    return False


@dataclass
class Toolset:
    full_path: str
    identifier: str

    def __lt__(self, other):
        return self.identifier > other.identifier


def find_toolsets(msvc_path : str) -> List[Toolset]:
    toolsets = []
    search_subpath = 'Msbuild\\Microsoft\\VC'
    search_path = os.path.join(msvc_path, search_subpath)
    if os.path.exists(search_path):
        for root, _, files in os.walk(search_path):
            if 'Toolset.props' in files:
                identifier = os.path.basename(root)
                if identifier.startswith('v'):
                    toolsets.append(Toolset(full_path=root, identifier=identifier))

    return toolsets


def unique_toolsets(toolsets:List[Toolset]):
    result = set()
    for entry in toolsets:
        result.add(entry.identifier)

    return list(result)


def get_toolset_ver(toolset:Toolset):
    if toolset.identifier.startswith('v'):
        return int(toolset.identifier[1:])
    return 0


# Value defined in _MSVC_VER
def get_cl_exe_compiler_version(cl_exe_path:str):
    out, err = call_process([cl_exe_path], capture=True, realtime=False)
    if err is not None:
        return None

    # Strip prefix
    version = ''
    for i in range(len(out)):
        if out[i:i+1].isdigit():
            version = out[i:]
            break

    # Strip suffix
    version = version.split()[0]

    return version


# Filters out legacy versions of toolsets, leaving only the latest one
def filter_legacy_toolsets(msvc_path : str, toolsets: List[Toolset]) -> List[Toolset]:
    msvc_path = os.path.join(msvc_path, 'Msbuild\\Microsoft\\VC\\')
    selected_version = ''
    result = []

    # Filter out legacy toolsets
    for tool in toolsets:
        if tool.full_path.startswith(msvc_path):
            tmp_path = tool.full_path[len(msvc_path):]
            first_slash_idx = tmp_path.find('\\')
            tmp_path = tmp_path[:first_slash_idx]
            if tmp_path > selected_version:
                selected_version = tmp_path
    for tool in toolsets:
        if selected_version in tool.full_path:
            result.append(tool)

    return result


def get_registry_key(storage : str, key : str, entry : str) -> Optional[Any]:
    try:
        hkey = winreg.OpenKey(storage, key)
    except:
        return None
    else:
        try:
            value, _ = winreg.QueryValueEx(hkey, entry)
            return value
        except:
            return None
        finally:
            winreg.CloseKey(hkey)


@dataclass
class WindowsSDKPaths:
    version : str
    base_path : str
    include : str
    lib : str
    bin : str


def discover_win10_sdk():
    storages = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    key_paths = ['SOFTWARE\\Wow6432Node', 'SOFTWARE']

    def is_valid_sdk_ver(sdk_ver:str) -> bool:
        return sdk_ver.startswith('10.')

    for storage in storages:
        for key in key_paths:

            key_path = f'{key}\\Microsoft\\Microsoft SDKs\\Windows\\v10.0'
            install_dir = get_registry_key(storage, key_path, 'InstallationFolder')

            if install_dir and os.path.isdir(install_dir):
                include_dir = os.path.join(install_dir, 'include')

                sdk_versions = filter(is_valid_sdk_ver, os.listdir(include_dir))
                latest_sdk = max(sdk_versions)

                logger.Verbose(f"Possible Win10SDK {install_dir}\nlatest: {latest_sdk}\nall:{ ', '.join(sdk_versions) }")

                if os.path.isdir(os.path.join(include_dir, latest_sdk)) and latest_sdk.startswith('10.'):
                    windows_h = os.path.join(include_dir, latest_sdk, 'um', 'Windows.h')
                    if os.path.isfile(windows_h):
                        sdk = WindowsSDKPaths(
                            version=latest_sdk,
                            base_path=install_dir,
                            include=os.path.join(install_dir, 'Include', latest_sdk),
                            lib=os.path.join(install_dir, 'Lib', latest_sdk),
                            bin=os.path.join(install_dir, 'bin', latest_sdk),
                        )
                        return sdk
    return None


def discover_msvc(host_arch: EArch, vs_instances) -> List[ToolchainDefinition]:
    toolchains : List[ToolchainDefinition] = []

    default_vc_path = 'VC\\Tools\\MSVC'
    default_bin_path = 'bin'
    default_lib_path = 'lib'
    default_include_paths = ['include', 'atlmfc\\include']
    default_compiler_msvc = 'cl.exe'
    default_linker_msvc = 'link.exe'
    default_librarian_msvc = 'lib.exe'

    additional_include_dirs = [
        'VC\\Auxiliary\\VS\\include',
        'VC\\Auxiliary\\VS\\UnitTest\\include'
    ]

    default_extra_files = [
        'c1.dll',
        'c2.dll',
        'c1xx.dll',
        '1033\\clui.dll',
        'msobj140.dll',
        'mspdb140.dll',
        'mspdbsrv.exe',
        'mspdbcore.dll',
        'mspft140.dll',
        'msvcp140.dll',
        'vcruntime140.dll',
        'vccorlib140.dll'
    ]

    default_link_libraries = [
        'kernel32'
        'user32'
        'gdi32'
        'winspool'
        'comdlg32'
        'advapi32'
        'shell32'
        'ole32'
        'oleaut32'
        'uuid'
        'odbc32'
        'odbccp32'
        'delayimp'
    ]

    for vs_itr in vs_instances:
        installation_path = vs_itr['installationPath']
        vs_ide_version = vs_itr['installationVersion']
        vc_tools = os.path.join(installation_path, default_vc_path)
        vs_version = vs_itr['catalog']['productLineVersion']

        available_toolsets = unique_toolsets(find_toolsets(installation_path))

        if os.path.exists(vc_tools):

            vc_versions = get_subdirs(vc_tools)
            vc_ver = max(vc_versions)

            # for vc_ver in vc_versions:
            vc_ver_basepath = os.path.join(vc_tools, vc_ver)
            vc_ver_binpath = os.path.join(vc_ver_basepath, default_bin_path)
            vc_ver_libpath = os.path.join(vc_ver_basepath, default_lib_path)

            for host in get_subdirs(vc_ver_binpath):
                if is_current_host(host, host_arch):
                    for arch in get_subdirs(os.path.join(vc_ver_binpath, host)):

                        msvc_name = vc_ver.replace('.','_')
                        arch_bin_fullpath = os.path.join(vc_ver_binpath, host, arch)
                        arch_lib_fullpath = os.path.join(vc_ver_libpath, arch)

                        msvc_ver = get_cl_exe_compiler_version(os.path.join(arch_bin_fullpath, default_compiler_msvc))
                        if msvc_ver is None:
                            continue

                        toolchain_name = f'{ECompilerFamily.MSVC.name}_{arch}_vs{vs_version}_v{msvc_name}'

                        includes = []
                        includes += [ os.path.join(vc_ver_basepath, inc) for inc in default_include_paths ]
                        includes += [ os.path.join(installation_path, inc) for inc in additional_include_dirs ]

                        # TODO: maybe this should be separate for compiler, librarian and linker?
                        path_envs = []
                        path_envs += [ arch_bin_fullpath ]

                        machine_linker_options = f'/MACHINE:{arch} '

                        compiler = ToolchainDefinition.create(
                            toolchain_name,
                            os.path.join(arch_bin_fullpath, default_compiler_msvc),
                            os.path.join(arch_bin_fullpath, default_librarian_msvc),
                            os.path.join(arch_bin_fullpath, default_linker_msvc),

                            arch=arch,

                            version=Version(msvc_ver),
                            ide_version=Version(vs_ide_version),
                            vs_install_path=installation_path,

                            Toolset=available_toolsets,

                            PathEnv=path_envs,

                            LinkerOptions=machine_linker_options,

                            LinkerPaths=[
                                arch_lib_fullpath,
                                arch_bin_fullpath,
                            ],

                            ExtraFiles = default_extra_files,

                            RequiredFiles=[],
                            IncludeDirectories=includes,
                            Defines=[]
                        )
                        toolchains.append(compiler)

    return toolchains


def get_clang_version(clang_exe_path: str) -> Optional[str]:
    out, err = call_process([clang_exe_path, '--version'], capture=True, realtime=False)
    if err is not None:
        return None

    version_prefix = 'clang version '
    version = out[len(version_prefix):]
    version = version.split()[0]

    return version


def discover_clang(host_arch:EArch, vs_instances) -> List[ToolchainDefinition]:
    # We need to find visual studio installations anyway
    # But how to handle standalone LLVM? Ignore it? Or match with what version?
    # All of them? The latest? Per toolset?

    # There is a thing I cannot find documentation about
    # Seems the Clang toolset exists in two versions per visual studio installation
    #   egx. 2022 has v170 and v160 folders with Clang
    #    and 2019 has v160 and v150
    # We don't want th
    # toolsets = filter_legacy_toolsets(installation_path, toolsets)

    # Find VS installations
    # Find Clang from visual studios

    # Find standalone LLVM installation
    # Match with vs toolsets

    # clang.exe will work as an compiler, librarian and linker
    # but we need link.exe to be present in path when calling the compiler
    # how on earth would we do that in fastbuild..?
    # Compiler in fastbuild has environment option!

    # TODO: We need to pass Environment from Compiler to DLLs, Libraries and Execs!
    # This will set correct PATH with linker.exe
    toolchains : List[ToolchainDefinition] = []

    default_msvc_path = 'VC\\Tools\\MSVC'
    default_llvm_path = 'VC\\Tools\\Llvm'
    default_bin_path = 'bin'
    default_lib_path = 'lib'
    default_llvm_include_path = 'include'
    default_msvc_include_paths = ['include', 'atlmfc\\include']
    default_compiler_clang = 'clang.exe'
    default_librarian_clang = 'llvm-ar.exe'
    default_linker_clang = 'lld-link.exe'
    default_compiler_msvc = 'cl.exe'
    default_linker_msvc = 'link.exe'

    additional_include_dirs = [
        'VC\\Auxiliary\\VS\\include',
        'VC\\Auxiliary\\VS\\UnitTest\\include'
    ]

    default_extra_files = [
        'c1.dll',
        'c2.dll',
        'c1xx.dll',
        '1033\\clui.dll',
        'msobj140.dll',
        'mspdb140.dll',
        'mspdbsrv.exe',
        'mspdbcore.dll',
        'mspft140.dll',
        'msvcp140.dll',
        'vcruntime140.dll',
        'vccorlib140.dll'
    ]

    standalone_clangs = []

    def try_create_clang_toolchain(clang_exe_path, msvc_ver_basepath, msvc_host, msvc_arch, vs_version, toolset:Toolset) -> Optional[ToolchainDefinition]:
        clang_ver = get_clang_version(clang_exe_path)
        if clang_ver is None:
            return None

        vc_ver_binpath = os.path.join(msvc_ver_basepath, default_bin_path)
        vc_ver_libpath = os.path.join(msvc_ver_basepath, default_lib_path)
        msvc_arch_bin_fullpath = os.path.join(vc_ver_binpath, msvc_host, msvc_arch)
        msvc_arch_lib_fullpath = os.path.join(vc_ver_libpath, msvc_arch)
        msvc_linker_exe = os.path.join(msvc_arch_bin_fullpath, default_linker_msvc)

        msvc_ver = get_cl_exe_compiler_version(os.path.join(msvc_arch_bin_fullpath, default_compiler_msvc))
        if msvc_ver is None:
            return None

        clang_ver_name = clang_ver.replace('.','_')

        clang_bin_dir = os.path.dirname(clang_exe_path)
        clang_base_dir = os.path.dirname(clang_bin_dir)
        clang_lib_dir = os.path.join(clang_base_dir, default_lib_path)
        clang_include_dir = os.path.join(clang_base_dir, default_llvm_include_path)
        clang_librarian_exe = os.path.join(clang_bin_dir, default_librarian_clang)
        clang_linker_clang = os.path.join(clang_bin_dir, default_linker_clang)

        compiler_name = f"{ECompilerFamily.CLANG.name}_{msvc_arch}_vs{vs_version}_v{clang_ver_name}"

        includes = [ clang_include_dir ]
        includes += [ os.path.join(msvc_ver_basepath, inc) for inc in default_msvc_include_paths ]
        includes += [ os.path.join(installation_path, inc) for inc in additional_include_dirs ]

        # TODO: maybe this should be separate for compiler, librarian and linker?
        path_envs = []
        path_envs += [ clang_bin_dir, msvc_arch_bin_fullpath ]

        machine_linker_options = f'/MACHINE:{msvc_arch} '

        sem_msvc_ver = Version(msvc_ver)
        msvc_compat_options = f"-fms-compatibility-version={sem_msvc_ver.major}{sem_msvc_ver.minor} "

        return ToolchainDefinition.create(
            compiler_name,
            clang_exe_path,
            clang_librarian_exe,
            msvc_linker_exe,

            CompilerOptions = msvc_compat_options,
            LinkerOptions = machine_linker_options,

            arch = msvc_arch,
            version = Version(clang_ver),
            ide_version = Version(vs_ide_version),
            vs_install_path = installation_path,

            Toolset = [ toolset.identifier ],
            PathEnv = path_envs,
            ExtraFiles = default_extra_files,

            LinkerPaths = [
                clang_lib_dir,
                clang_bin_dir,
                msvc_arch_lib_fullpath,
                msvc_arch_bin_fullpath,
            ],

            RequiredFiles=[],
            IncludeDirectories=includes,
            Defines=[]
        )

    env_path = get_env_path()
    for path in env_path:
        for file in get_files(path): 
            if file.find(default_compiler_clang) != -1:
                clang_path = os.path.join(path, file)
                standalone_clangs.append(clang_path)

    for vs_itr in vs_instances:
        installation_path = vs_itr['installationPath']
        vs_ide_version = vs_itr['installationVersion']
        msvc_tools = os.path.join(installation_path, default_msvc_path)
        llvm_tools = os.path.join(installation_path, default_llvm_path)
        vs_version = vs_itr['catalog']['productLineVersion']

        toolsets = find_toolsets(installation_path)
        latest_toolset = max(toolsets, key=get_toolset_ver)

        logger.Verbose(f"For VS {installation_path} picked {latest_toolset} from found toolsets:\n{[t.identifier for t in toolsets]}")

        msvc_versions = get_subdirs(msvc_tools)
        latest_msvc = max(msvc_versions)

        # for vc_ver in vc_versions:
        msvc_ver_basepath = os.path.join(msvc_tools, latest_msvc)
        vc_ver_binpath = os.path.join(msvc_ver_basepath, default_bin_path)

        if os.path.exists(msvc_tools):

            for msvc_host in get_subdirs(vc_ver_binpath):
                if is_current_host(msvc_host, host_arch):
                    for msvc_arch in get_subdirs(os.path.join(vc_ver_binpath, msvc_host)):

                        # Standalone Clang
                        for clang_entry in standalone_clangs:
                            compiler = try_create_clang_toolchain(clang_entry, msvc_ver_basepath, msvc_host, msvc_arch, vs_version, latest_toolset)
                            if compiler is None:
                                continue

                            toolchains.append(compiler)

                        # Bundled Clang
                        if os.path.exists(llvm_tools):
                            for host in get_subdirs(llvm_tools):
                                if is_current_host(host, host_arch):
                                    if host == default_bin_path:
                                        host = ''

                                    clang_dir = os.path.join(llvm_tools, host, default_bin_path)
                                    clang_exe = os.path.join(clang_dir, default_compiler_clang)

                                    compiler = try_create_clang_toolchain(clang_exe, msvc_ver_basepath, msvc_host, msvc_arch, vs_version, latest_toolset)
                                    if compiler is None:
                                        continue

                                    toolchains.append(compiler)

    return toolchains


def discover_toolchain_list(host_arch: EArch) -> List[ToolchainDefinition] :
    vswhere_path = None

    try:
        vswhere_path = vswhere.find_vswhere()
    except Exception:
        pass

    if vswhere_path is None:
        logger.Warning("Unable to find vswhere executable, VS toolchains not discovered")
        return []

    vs_instances = json.loads(vswhere.call_vswhere(vswhere_path))
    if vs_instances is None:
        logger.Warning("vswhere found no VS installations")
        return []

    toolchains : List[ToolchainDefinition] = []
    toolchains += discover_msvc(host_arch, vs_instances)
    toolchains += discover_clang(host_arch, vs_instances)

    win10_sdk = discover_win10_sdk()

    if win10_sdk is not None:
        logger.Verbose(f"Found Win10SDK in {win10_sdk.base_path}")
        for toolchain in toolchains:
            # This should work for clang/clangCL too
            #if toolchain.CompilerFamily == ECompilerFamily.MSVC:
            toolchain.LinkerPaths.append(f'{win10_sdk.lib}\\um\\{toolchain.arch.lower()}')
            toolchain.LinkerPaths.append(f'{win10_sdk.lib}\\ucrt\\{toolchain.arch.lower()}')
            toolchain.IncludeDirectories.append(f'{win10_sdk.include}\\shared')
            toolchain.IncludeDirectories.append(f'{win10_sdk.include}\\um')
            toolchain.IncludeDirectories.append(f'{win10_sdk.include}\\ucrt')

    return toolchains
