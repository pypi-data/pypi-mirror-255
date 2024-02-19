from typing import Dict, List, Tuple, Optional

from zetsubou.commands.command_context import CommandContext
from zetsubou.conan.to_conan import toolsets_from_settings, msvc_version_to_conan
from zetsubou.conan.conan import get_conan_settings
from zetsubou.project.model.platform import Platform
from zetsubou.project.model.platform_enums import EArch, ESystem, EVersionSelector
from zetsubou.project.model.toolchain import Toolchain, ToolchainDefinition
from zetsubou.project.model.toolchain_enums import ECompilerFamily
from zetsubou.project.model.toolchain_profile import IToolchainProfile, Windows_ToolchainProfile
from zetsubou.utils import logger
from zetsubou.utils.common import is_in_enum


def is_second_newer_toolchain(first:ToolchainDefinition, second:ToolchainDefinition) -> bool:
    if first.CompilerFamily == ECompilerFamily.MSVC:
        if first.ide_version < second.ide_version:
            return True

    return first.version < second.version


# MSVC entries need to reparse due to how conan handles them
# Egx. 19.35 becomes 193.5 on conan
def is_matching_compiler_version(toolchain:ToolchainDefinition, versions:List[str]) -> bool:
    if toolchain.CompilerFamily == ECompilerFamily.MSVC:
        if msvc_version_to_conan(toolchain.version)[0] in versions:
            return True
    else:
        if str(toolchain.version.major) in versions:
            return True


class _ToolchainResult:
    definition: ToolchainDefinition
    filter: IToolchainProfile

    def __init__(self, defs:ToolchainDefinition, fltr:IToolchainProfile):
        self.definition = defs
        self.filter = fltr


def discover_toolchain_list(context: CommandContext) -> Optional[Tuple[Dict[str, List[Toolchain]], List[ToolchainDefinition]]] :
    system_toolchains   : List[ToolchainDefinition]  = discover_toolchain_by_system(context.host_system, context.host_arch)
    platform_toolchains : Dict[str, List[Toolchain]] = {}

    if len(system_toolchains) == 0:
        logger.CriticalError(f"No system toolchains detected on {context.host_system} {context.host_arch}!")
        return None

    conan_settings = get_conan_settings()

    # There were severe issues which toolchains on builders, so this code is left for convinience
    enable_toolchain_trace = False
    def trace_skipped_toolchain(tool_def : ToolchainDefinition, reason : str):
        logger.Verbose(f"TRACE: skipped toolchain '{tool_def.name}' ver '{tool_def.version}' reason: {reason}")

    if enable_toolchain_trace:
        logger.SetLogLevel(logger.ELogLevel.Verbose)

    for platform in context.project_template.platforms:
        compatible_toolchains = set()

        for tool_filter in context.project_template.profile.toolchains:
            # Single filter might output many toolchains (egx. with version set to all)
            latest_by_compiler : Optional[_ToolchainResult] = None

            logger.Verbose(f'Filter family={tool_filter.compiler_family} ver={tool_filter.compiler_version} target_arch={tool_filter.target_arch} toolset={tool_filter.toolset}')

            for tool_def in system_toolchains:
                if not is_in_enum(tool_def.arch, EArch):
                    trace_skipped_toolchain(tool_def, 'Unknown arch')
                    continue # Unknown arch

                if EArch[tool_def.arch] != platform.target_arch:
                    trace_skipped_toolchain(tool_def, 'Arch mismatch')
                    continue # Arch mismatch

                if tool_def.CompilerFamily != tool_filter.compiler_family:
                    trace_skipped_toolchain(tool_def, 'Family mismatch')
                    continue # Family mismatch

                if tool_filter.compiler_version == EVersionSelector.latest:
                    if latest_by_compiler is None:
                        latest_by_compiler = _ToolchainResult(tool_def, tool_filter)
                    elif is_second_newer_toolchain(latest_by_compiler.definition, tool_def):
                        latest_by_compiler = _ToolchainResult(tool_def, tool_filter)
                    else:
                        trace_skipped_toolchain(tool_def, 'Not latest version')
                        continue

                elif not is_matching_compiler_version(tool_def, tool_filter.compiler_version):
                    trace_skipped_toolchain(tool_def, 'Version mismatch')
                    continue # Version mismatch

                compatible_toolchains.add(_ToolchainResult(tool_def, tool_filter))

            if latest_by_compiler is not None:
                compatible_toolchains.add(latest_by_compiler)

        def result_to_toolchain(tres:_ToolchainResult) -> List[Toolchain]:
            toolchains = []

            filter_by_toolset = isinstance(tres.filter, Windows_ToolchainProfile)
            if filter_by_toolset:

                def_toolsets = tres.definition.Toolset
                conan_toolsets = toolsets_from_settings(conan_settings, tres.definition.CompilerFamily)
                if conan_toolsets is not None:
                    def_toolsets = conan_toolsets.intersection(def_toolsets)

                if tres.filter.toolset == EVersionSelector.latest:
                    latest_toolset = max(def_toolsets)
                    tool = Toolchain(f"{tres.definition.name}_{latest_toolset}", tres.filter, tres.definition, toolset=latest_toolset)
                    toolchains.append(tool)

                else:
                    for toolset in tres.definition.Toolset:
                        tool = Toolchain(f"{tres.definition.name}_{toolset}", tres.filter, tres.definition, toolset=toolset)
                        toolchains.append(tool)

            else:
                toolchains.append(Toolchain(tres.definition.name, tres.filter, tres.definition, ''))

            return toolchains

        toolchain_objs = set()
        for res in map(result_to_toolchain, compatible_toolchains):
            toolchain_objs = toolchain_objs.union(res)

        platform_toolchains[platform.platform] = list(toolchain_objs)

    def system_toolchains_to_string():
        toolchains_labels = []
        for tool_def in system_toolchains:
            toolchains_labels.append(f"{tool_def.name} ver={tool_def.version}")

        prefix = '\n  - '
        label = prefix.join(toolchains_labels)
        return f"Available system toolchains:{prefix}{label}\n"

    if len(platform_toolchains) == 0:
        logger.CriticalError(f"No platform toolchains detected on {context.host_system} {context.host_arch}!")
        logger.Error(system_toolchains_to_string())
        return None

    for plat, tools in platform_toolchains.items():
        if len(tools) == 0:
            logger.CriticalError(f"No toolchains on platform '{plat}' detected on {context.host_system} {context.host_arch}!")
            logger.Error(system_toolchains_to_string())
            return None
        elif logger.IsVisible(logger.ELogLevel.Verbose):
            logger.Verbose(f"TRACE: Found platform {plat} toolchains:")
            for tool_def in tools:
                logger.Verbose(f"TRACE: {tool_def.name} ver={tool_def.definition.version} toolset={tool_def.toolset}")

    return (platform_toolchains, system_toolchains)


def discover_toolchain_by_system(host_system: ESystem, host_arch: EArch) -> List[ToolchainDefinition] :
    if host_system == ESystem.Windows:
        from zetsubou.system.windows import windows
        return windows.discover_toolchain_list(host_arch)
    else:
        raise EnvironmentError(f'Sorry, discovering toolchains on \"{host_system.name}\" arch \"{host_arch.name}\" is not currently supported!')


def filter_toolchains_by_target_arch(toolchain:ToolchainDefinition, platforms:List[Platform]):
    for plat in platforms:
        if not is_in_enum(toolchain.arch, EArch):
            logger.Warning(f"Unknown arch '{toolchain.arch}' for toolchain '{toolchain.name}'")
            return False

        if EArch[toolchain.arch] == plat.target_arch:
            return True

    return False
