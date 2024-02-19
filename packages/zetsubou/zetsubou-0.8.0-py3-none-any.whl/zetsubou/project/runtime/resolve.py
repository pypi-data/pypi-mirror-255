from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field, fields, is_dataclass
from typing_inspect import get_origin
import os
import fnmatch, typing_inspect
from zetsubou.project.model.config_string import EDefaultConfigSlots
from zetsubou.project.model.configuration import Configuration
from zetsubou.project.model.filter import TargetFilter

from zetsubou.project.base_context import BaseContext
from zetsubou.project.model.kind import ETargetKind
from zetsubou.project.config_matrix import ConfigVariant, ConfigMatrix
from zetsubou.project.runtime.project_loader import ProjectTemplate
from zetsubou.project.model.target import PathList, Target, TargetData, Source, TargetReference, PropertyList
from zetsubou.project.model.toolchain import Toolchain
from zetsubou.utils import logger
from bentoudev.dataclass.base import is_clazz_list


def PrintDataclass(clazz, id = 0):
    prefix = ''
    for _ in range(id):
        prefix += ' '

    if is_dataclass(clazz):
        print(f'{prefix}Class: {clazz.__name__}')
        for f in fields(clazz):
            print(f'{prefix}name: {f.name}, type: {f.type}')
            PrintDataclass(f.type, id + 4)
    else:
        if typing_inspect.is_generic_type(clazz):
            if typing_inspect.get_origin(clazz) == list:
                subtype = clazz.__args__[0]
                print(f'{prefix}subtype: {subtype}')
                PrintDataclass(subtype, id + 4)
            else:
                print(f'{prefix }Unhandled type {clazz}')


def config_matches_variant(config: str, config_matrix: ConfigVariant) -> bool:
    if config == '*':
        return True

    conf_lower = config.lower()
    matrix_lower = config_matrix.config_string.lower()
    return fnmatch.fnmatch(matrix_lower, conf_lower)


def config_matches_filter(filter: TargetFilter, config_variant : ConfigVariant, target : Target, config: Configuration, toolchain:Toolchain) -> bool:
    if (
            config_matches_variant(filter.config_string, config_variant) and
            (filter.kind is None or target.config.kind in filter.kind) and
            # TODO: FIXME: This is windows only!!!
            (filter.runtime_library is None or toolchain.profile.runtime in filter.runtime_library) and
            (filter.base_configuration is None or config.base_configuration in filter.base_configuration)
       ):
        return True
    return False


def append_list(target: Optional[List[Any]], source: Optional[List[Any]]):
    if target is None:
        raise ValueError('append_list target must not be None!')
    if source is not None:
        target += source


def append_source(target: Source, source: Optional[Source]):
    if source is not None:
        append_list(target.paths, source.paths)
        append_list(target.patterns, source.patterns)


def append_properties(target: PropertyList, source: Optional[PropertyList]):
    if source is not None:
        append_list(target.interface, source.interface)
        append_list(target.public, source.public)
        append_list(target.private, source.private)


@dataclass
class TargetVariant(TargetData):
    config_variant: ConfigVariant = None
    compiler: str = ''
    platform: str = ''

    def __init__(self, config_variant: ConfigVariant):
        TargetData.__init__(self)
        self.config_variant = config_variant

        def init_sources(src: Source):
            src.paths = []
            src.patterns = []

        def init_properties(prop: PropertyList):
            prop.interface = []
            prop.public = []
            prop.private = []

        for data_field in fields(TargetData):
            # Handle Optionals
            field_type = data_field.type

            if typing_inspect.is_optional_type(field_type):
                field_type = field_type.__args__[0]

            self_value = getattr(self, data_field.name)

            if is_clazz_list(field_type):
                self_value = list()
            else:
                self_value = field_type()

                if issubclass(field_type, Source):
                    init_sources(self_value)
                elif issubclass(field_type, PropertyList):
                    init_properties(self_value)

            setattr(self, data_field.name, self_value)


    def apply(self, data: TargetData):

        for data_field in fields(TargetData):
            # Handle Optionals
            field_type = data_field.type
            if typing_inspect.is_optional_type(field_type):
                field_type = field_type.__args__[0]

            self_value = getattr(self, data_field.name)
            other_value = getattr(data, data_field.name)

            if is_clazz_list(field_type):
                append_list(self_value, other_value)
            else:
                if issubclass(field_type, Source):
                    append_source(self_value, other_value)
                elif issubclass(field_type, PathList):
                    # TODO: Needs fix, cannot blindly append relative paths
                    append_properties(self_value, other_value)
                else:
                    append_properties(self_value, other_value)

            setattr(self, data_field.name, self_value)


@dataclass
class ResolvedTarget:
    name: str
    target: Target
    variants: Dict[str, TargetVariant]

    def get_kind(self) -> ETargetKind:
        return self.target.config.kind


@dataclass
class ResolveContext(BaseContext):
    project: ProjectTemplate = None
    target_cache: Dict[str, ResolvedTarget] = field(default_factory=dict)
    resolved_targets: List[ResolvedTarget] = field(default_factory=list)

    @classmethod
    def from_base(cls, source : BaseContext):
        result = ResolveContext()
        result.__dict__.update(source.__dict__)
        return result

    def find_target_variant(self, target: Target, config_str: str) -> Optional[TargetVariant]:
        if target.target in self.target_cache:
            if config_str in self.target_cache[target.target].variants:
                return self.target_cache[target.target].variants[config_str]
        return None

    def add_target_variant(self, target: Target, config_variant: ConfigVariant, target_variant: TargetVariant):
        resolved_target: Optional[ResolvedTarget] = None
        if target.target in self.target_cache:
            resolved_target = self.target_cache[target.target]
        else:
            resolved_target = ResolvedTarget(
                name=target.target,
                target=target,
                variants={}
            )
            self.target_cache[target.target] = resolved_target
            self.resolved_targets.append(resolved_target)
        resolved_target.variants[config_variant.config_string] = target_variant


def append_paths(target: Optional[List[Any]], source: Optional[List[Any]], base_path : str, dep_path : str, fs_root : str):
    if target is None:
        raise ValueError('append_list target must not be None!')
    if source is not None:
        base_fullpath = os.path.normpath(os.path.join(fs_root, base_path))
        dep_fullpath = os.path.normpath(os.path.join(fs_root, dep_path))
        rel_dep_to_base = os.path.relpath(os.path.dirname(dep_fullpath), os.path.dirname(base_fullpath))
        target += [ os.path.join(rel_dep_to_base, i) for i in source ]


def apply_slot(context: ResolveContext, target_variant: TargetVariant, config_variant: ConfigVariant, slot_name: str, slot_value: str, target: Target, config: Configuration, toolchain:Toolchain):
    if EDefaultConfigSlots.toolchain.name == slot_name:
        target_variant.compiler = slot_value

    elif EDefaultConfigSlots.platform.name == slot_name:
        platform = context.project.find_platform(slot_value)
        target_variant.platform = platform.platform
        target_variant.apply(platform)

        for plat_filter in platform.filters:
            if config_matches_filter(plat_filter.filter, config_variant, target, config, toolchain):
                target_variant.apply(plat_filter)

    elif EDefaultConfigSlots.configuration.name == slot_name:
        config = context.project.find_config(slot_value)
        target_variant.apply(config)

        for conf_filter in config.filters:
            if config_matches_filter(conf_filter.filter, config_variant, target, config, toolchain):
                target_variant.apply(conf_filter)


def apply_dependencies_refl(context: ResolveContext, target : Target, target_variant: TargetVariant, config_variant: ConfigVariant, config: Configuration, toolchain:Toolchain):
    target_cls_fields = fields(TargetData)
    target_source_path = target.get_loaded_from_file()

    accessors = [ 'private', 'public', 'interface' ]
    for access in accessors:
        deps : Optional[List[TargetReference]] = getattr(target_variant.dependencies, access)

        if deps is None:
            continue

        for dep_ref in deps:
            lnk_libs = getattr(target_variant.link_libraries, access)
            lnk_libs.append(dep_ref)
            setattr(target_variant.link_libraries, access, lnk_libs)

            dep_variant = create_target_variant(context, dep_ref.target, config_variant, config, toolchain)
            dep_source_path = dep_ref.target.get_loaded_from_file()

            imported_dep_target : bool = dep_ref.target.config.kind == ETargetKind.IMPORTED_TARGET
            custom_dep_target   : bool = dep_ref.target.config.kind == ETargetKind.BUILD_STEP

            # For custom build steps, manually make sure that they are executed before target is built
            if custom_dep_target:
                target_variant.build_require.append(dep_ref)

            if imported_dep_target:
                # Manually pass imported includes as system ones
                sys_inc_value_access = getattr(target_variant.system_includes, access)

                append_paths(sys_inc_value_access, dep_variant.includes.public, target_source_path, dep_source_path, context.fs_root)
                append_paths(sys_inc_value_access, dep_variant.includes.interface, target_source_path, dep_source_path, context.fs_root)

                append_paths(sys_inc_value_access, dep_variant.system_includes.public, target_source_path, dep_source_path, context.fs_root)
                append_paths(sys_inc_value_access, dep_variant.system_includes.interface, target_source_path, dep_source_path, context.fs_root)

                setattr(target_variant.system_includes, access, sys_inc_value_access)

            for data_field in target_cls_fields:
                dep_field_holder = getattr(dep_variant, data_field.name)

                if dep_field_holder is None:
                    continue

                field_value = getattr(target_variant, data_field.name)

                # Handle Optionals
                field_type = data_field.type
                if typing_inspect.is_optional_type(field_type):
                    field_type = field_type.__args__[0]

                if field_type == list or get_origin(field_type) == list:
                    append_list(field_value, dep_field_holder)

                elif issubclass(field_type, PropertyList):
                    dep_field_public = getattr(dep_field_holder, 'public')
                    dep_field_iface = getattr(dep_field_holder, 'interface')
                    field_value_access = getattr(field_value, access)

                    if issubclass(field_type, PathList):
                        # Includes for imported targets have to be handled manually
                        if not (imported_dep_target and data_field.name.find('includes') != -1):
                            append_paths(field_value_access, dep_field_public, target_source_path, dep_source_path, context.fs_root)
                            append_paths(field_value_access, dep_field_iface, target_source_path, dep_source_path, context.fs_root)
                    else:
                        append_list(field_value_access, dep_field_public)
                        append_list(field_value_access, dep_field_iface)

                    setattr(field_value, access, field_value_access)

                setattr(target_variant, data_field.name, field_value)


def create_target_variant(context: ResolveContext, target: Target, config_variant: ConfigVariant, config: Configuration, toolchain:Toolchain) -> TargetVariant:
    target_variant = context.find_target_variant(target, config_variant.config_string)
    if target_variant is None:
        target_variant = TargetVariant(config_variant)
        target_variant.apply(target)

        for filter_data in target.filters:
            if config_matches_filter(filter_data.filter, config_variant, target, config, toolchain):
                target_variant.apply(filter_data)

        for slot_name, slot_value in config_variant.slots.items():
            apply_slot(context, target_variant, config_variant, slot_name, slot_value, target, config, toolchain)

        for rule in context.project.rules:
            for filter_data in rule.filters:
                if config_matches_filter(filter_data.filter, config_variant, target, config, toolchain):
                    target_variant.apply(filter_data)

        apply_dependencies_refl(context, target, target_variant, config_variant, config, toolchain)

    context.add_target_variant(target, config_variant, target_variant)
    return target_variant


def resolve_target_variants(context: ResolveContext, config_matrix: ConfigMatrix, targets: List[Target]):
    for target in targets:
        for config_variant in config_matrix.variants:
            toolchain = context.project.find_toolchain(config_variant.get_slot(EDefaultConfigSlots.platform), config_variant.get_slot(EDefaultConfigSlots.toolchain))
            config = context.project.find_config(config_variant.get_slot(EDefaultConfigSlots.configuration))
            create_target_variant(context, target, config_variant, config, toolchain)

    return context.resolved_targets
