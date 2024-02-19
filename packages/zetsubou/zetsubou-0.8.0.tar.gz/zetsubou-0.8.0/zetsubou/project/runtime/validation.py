from typing import List, Optional
from zetsubou.project.model.cli_tool import CommandlineTool
from zetsubou.project.model.kind import ETargetKind
from zetsubou.project.model.target import Dependencies, Target, TargetReference, find_target
from zetsubou.project.model.toolchain_profile import IToolchainProfile, Profile
from zetsubou.project.model.toolchain import ECppStandard, ICompiler, get_compiler_by_family
from zetsubou.utils.common import foreach
from zetsubou.utils.error import ProjectError

import bentoudev.dataclass.base as base


class ValidationContext:
    error_format: base.EErrorFormat


def find_unresolved_target_references(ctx:ValidationContext, targets: List[Target], deps: Optional[List[TargetReference]]) -> List[TargetReference]:
    failed_refs = []
    if deps:
        for ref in deps:
            found_target = find_target(targets, ref.name)
            if found_target is None:
                failed_refs.append(ref)
            else:
                ref.target = found_target
    return failed_refs


def validate_duplicates(ctx:ValidationContext, targets: List[Target]):
    visited = dict()
    for target in targets:
        if target.target in visited:
            tmp_msg = target.format_field_message('target', 'error', f"Duplicated target name '{target.target}'!", ctx.error_format)
            err_msg = f"{tmp_msg}\n'{visited[target.target].format_field_message('target', '', 'Second', ctx.error_format)}'"
            raise ProjectError(err_msg)
        else:
            visited[target.target] = target


def validate_cyclic_dependency(ctx:ValidationContext, targets: List[Target]):
    visited = dict()

    def visit_target(in_target):
        nonlocal visited

        target = in_target

        if isinstance(in_target, TargetReference):
            target = in_target.target

        if target.target in visited:
            target_path = []
            msg = []

            for path_element, path_ref in visited.items():
                target_path.append(path_element)
                target_path.append(' -> ')

                if isinstance(path_ref, TargetReference):
                    msg.append(path_ref.format_message('', '\nReferenced here', ctx.error_format))
                    msg.append('\n')

            target_path.append(f'{target.target}')

            path_msg = ''.join(target_path)
            ref_msg = ''.join(msg)

            main_msg = in_target.format_message('error', f"Cyclic dependency to target '{target.target}' through '{path_msg}'", ctx.error_format)
            err_msg = f'{main_msg}\n{ref_msg}'
            raise ProjectError(err_msg)

        def visit_dependencies(t: Target, d: Dependencies):
            foreach(d.interface, visit_target)
            foreach(d.public, visit_target)
            foreach(d.private, visit_target)

        visited[target.target] = in_target

        if target.dependencies is not None:
            visit_dependencies(target, target.dependencies)

        if target.filters is not None:
            for f in target.filters:
                if f.dependencies is not None:
                    visit_dependencies(target, f.dependencies)

        del visited[target.target]

    for target in targets:
        visit_target(target)


def validate_unresolved_target_dependencies(ctx:ValidationContext, target_name: str, dependencies, targets: List[Target]):
    if dependencies is not None:
        for name, dep_list in {
            'interface': dependencies.interface,
            'public': dependencies.public,
            'private': dependencies.private
        }.items():

            unresolved_refs = find_unresolved_target_references(ctx, targets, dep_list)

            if len(unresolved_refs) > 0:
                msg = ''
                for un_ref in unresolved_refs:
                    msg += un_ref.format_message('error', f"\nUnknown target '{un_ref.name}'", ctx.error_format)

                raise ProjectError(
                    f'Reference to undefined targets in \'{name}\' dependencies of target \'{target_name}\'{msg}')


def validate_targets_not_empty(ctx:ValidationContext, targets: List[Target]):
    if (len(targets)) == 0:
        raise ProjectError("Cannot load project with no targets!")


def validate_unresolved_targets(ctx:ValidationContext, targets: List[Target]):
    for target in targets:
        validate_unresolved_target_dependencies(ctx, target.target, target.dependencies, targets)
        for f in target.filters:
            validate_unresolved_target_dependencies(ctx, target.target, f.dependencies, targets)


def validate_custom_build_steps(ctx:ValidationContext, targets: List[Target]):
    for target in targets:
        if target.config.kind != ETargetKind.BUILD_STEP and target.config.compiler is not None:
            raise ProjectError(f'Custom compiler cannot be defined for target \'{target.target}\' of kind \'{target.config.kind.name}\'')
        elif target.config.kind == ETargetKind.BUILD_STEP and target.config.compiler is None:
            raise ProjectError(f'Custom compiler must be defined for target \'{target.target}\' of kind \'{target.config.kind.name}\'')


def validate_cli_tools(ctx:ValidationContext, targets : List[Target], cli_tools : List[CommandlineTool]):
    for target in targets:
        if target.config.kind == ETargetKind.BUILD_STEP:
            found_tool:bool = False
            for tool in cli_tools:
                if tool.name == target.config.compiler:
                    found_tool = True
                    break
            if not found_tool:
                raise ProjectError(f'Reference to undefined custom compiler \'{target.config.compiler}\' for target \'{target.target}\'')


def validate_targets(ctx:ValidationContext, targets : List[Target]):
    validate_targets_not_empty(ctx, targets)
    validate_unresolved_targets(ctx, targets)
    validate_duplicates(ctx, targets)
    validate_cyclic_dependency(ctx, targets)
    validate_custom_build_steps(ctx, targets)


##########################################################################


# def validate_compiler_duplicates(ctx:ValidationContext, platforms : List[Platform]):
#     for plat in platforms:
#         compiler_families = dict()
#         for tool_filter in plat.toolchains:
#             if tool_filter.family in compiler_families:
#                 first_occur = compiler_families[tool_filter.family].format_field_message('family', '', 'First referenced here', ctx.error_format)
#                 msg = tool_filter.format_field_message(
#                     'family',
#                     'error',
#                     f"Duplicated toolchain definition for '{tool_filter.family.name}'.\n{first_occur}", ctx.error_format)
#                 raise ProjectError(msg)
#             else:
#                 compiler_families[tool_filter.family] = tool_filter


def validate_cpp_standard(ctx:ValidationContext, toolchains : List[IToolchainProfile]):
    def built_supported_values(compiler_t:ICompiler):
        all_values = ECppStandard.__members__.items()
        allowed_values = []
        for value in all_values:
            if compiler_t.cpp_to_str(value[1]) is not None:
                allowed_values.append(value[0])
        return allowed_values

    for tool_filter in toolchains:
        compiler_t = get_compiler_by_family(tool_filter.compiler_family)
        if compiler_t.cpp_to_str(tool_filter.cppstd) is None:
            msg = tool_filter.format_field_message(
                    'cppstd',
                    'error',
                    f"Unsupported C++ version '{tool_filter.cppstd.name}' for compiler family '{tool_filter.compiler_family.name}'.\n"
                    f"Supported are: {', '.join(built_supported_values(compiler_t))}",
                    ctx.error_format)
            raise ProjectError(msg)


def validate_profile(ctx:ValidationContext, profile : Profile):
    # validate_compiler_duplicates(ctx, platforms)
    validate_cpp_standard(ctx, profile.toolchains)
