import os
from dataclasses import dataclass
from typing import List, Optional, Dict

import fs
from fs.base import FS

import importlib_resources as resources
import bentoudev.dataclass.base as base

from zetsubou.project.model.cli_tool import CommandlineTool
from zetsubou.project.model.config_string import EDefaultConfigSlots, VARIANT_STR_DELIMETER
from zetsubou.project.model.configuration import Configuration
from zetsubou.project.model.kind import ETargetKind
from zetsubou.project.model.platform import Platform
from zetsubou.project.model.project_template import CONFIG_STRING_DEPRECATED, Project
from zetsubou.project.model.toolchain_profile import Profile
from zetsubou.project.model.rule import Rule
from zetsubou.project.model.target import Target, find_target
from zetsubou.project.model.toolchain import ToolchainDefinition, Toolchain
from zetsubou.utils import logger, yaml_loader
from zetsubou.utils.common import is_in_enum, null_or_empty
from zetsubou.utils.error import ProjectError
from zetsubou.utils.file_cache import FileCache


class NoTraceError(Exception):
    pass


@dataclass
class ExternalConfig:
    profile_file: Optional[str] = None


@dataclass
class ProjectTemplate:
    project: Project
    profile: Optional[Profile]
    platforms: List[Platform]
    system_toolchains: List[ToolchainDefinition]
    platform_toolchains: Dict[str, List[Toolchain]]
    cli_tools: List[CommandlineTool]
    configurations: List[Configuration]
    rules: List[Rule]
    targets: List[Target]

    def find_target_by_file(self, filepath:str):
        for target in self.targets:
            if filepath == target.get_loaded_from_file():
                return target
        return None

    def find_target(self, name:str):
        return find_target(self.targets, name)

    def find_platform(self, name : str):
        for plat in self.platforms:
            if plat.platform == name:
                return plat
        return None

    def find_config(self, name : str):
        for conf in self.configurations:
            if conf.configuration == name:
                return conf
        return None

    def find_cli_tool(self, name : str):
        for tool in self.cli_tools:
            if tool.name == name:
                return tool
        return None

    def find_toolchain(self, platform_name: str, toolchain_name: str):
        toolchain_list : List[Toolchain] = self.platform_toolchains.get(platform_name, None)
        if toolchain_list is None:
            return None

        for tool in toolchain_list:
            if toolchain_name == tool.name:
                return tool
        return None

    def list_configurations(self):
        result = []
        for conf in self.configurations:
            result.append(conf.configuration)
        return result

    def list_platforms(self):
        result = []
        for plat in self.platforms:
            result.append(plat.platform)
        return result

    # This outputs invalid values - toolchains are dependent on their platforms!
    def list_toolchain(self):
        result = []
        for _, tools in self.platform_toolchains.items():
            names = [ t.name for t in tools ]
            result.extend(names)
        return result

    def slot_values(self) -> dict:
        result = {
            EDefaultConfigSlots.platform.name : self.list_platforms(),
            EDefaultConfigSlots.configuration.name : self.list_configurations(),
            EDefaultConfigSlots.toolchain.name : self.list_toolchain()
        }

        for option in self.project.options:
            result[option.name] = option.values

        return result

    def format_slot_string(self, slot_string, config_variant : str):
        slot_values, err = self.parse_config_variant(config_variant)
        if slot_values is None:
            raise ValueError(f"Unable to parse config variant '{config_variant}'. '{err}'")
        return slot_string.format(**slot_values)

    def get_slot_value(self, slot_to_access : str, conf_variant : str):
        slot = slot_to_access.name if isinstance(slot_to_access, EDefaultConfigSlots) else slot_to_access

        result, err = self.parse_config_variant(conf_variant)
        if result is None:
            raise ValueError(f"Unable to parse config variant '{conf_variant}'. {err}")

        if slot not in result:
            raise ValueError(f"No slot '{slot}' in config matrix!")

        return result[slot]

    def _fill_config_slots(self, parts:List[str]) -> (Optional[dict], str):
        domain = self.slot_values()
        result = dict()

        for slot, value in zip(EDefaultConfigSlots.__members__, parts):
            if value not in domain[slot]:
                return (None, f"Unknown value '{value}' in slot '{slot}'")

            result[slot] = value

        return (result, '')

    def parse_config_variant(self, variant_str:str) -> (Optional[dict], str):
        # Parse
        parts = variant_str.split(VARIANT_STR_DELIMETER)

        # Validate and fill
        if len(parts) != len(EDefaultConfigSlots.__members__):
            return (None, f"Invalid number of slots '{len(parts)}', expected '{len(EDefaultConfigSlots.__members__)}'")

        return self._fill_config_slots(parts)

    def parse_target_variant(self, variant_str:str) -> (Optional[dict], str):
        # Parse
        parts = variant_str.split(VARIANT_STR_DELIMETER)

        # NOTE: do we want to have target_kind at all?

        # Validate and fill
        if len(parts) != 1 + len(EDefaultConfigSlots.__members__):
            return (None, f"Invalid number of slots '{len(parts)}', expected '{1 + len(EDefaultConfigSlots.__members__)}'")

        result, err = self._fill_config_slots(parts[1:])
        if result is not None:
            target_name = parts[0]
            #target_kind = parts[1]

            #if not any(filter(lambda e : target_kind.startswith(e[0]), ETargetKind.__members__)):
            #    return (None, f"Unknown value '{target_kind}' in slot 'target_kind'")

            result['target'] = target_name
            # result['target_kind'] = target_kind

        return (result, err)

    def compile_target_variant_name(self, slots:dict) -> (Optional[str], str):
        default_slots = list(map(lambda m: m, EDefaultConfigSlots.__members__))
        allowed_slots = [ 'target', 'target_kind', 'config_variant' ] + default_slots # 'target_kind', 

        # Validate
        for name, _ in slots.items():
            if name not in allowed_slots:
                return (None, f"Unknown slot '{name}' provided.")

        try:
            if 'config_variant' in slots:
                target = slots['target']
                conf_var = slots['config_variant']

                slot_values = [target, conf_var]
                return (VARIANT_STR_DELIMETER.join(slot_values), '')

            else:
                target = slots['target']
                plat = slots[EDefaultConfigSlots.platform.name]
                conf = slots[EDefaultConfigSlots.configuration.name]
                tool = slots[EDefaultConfigSlots.toolchain.name]
                slot_values = [target, plat, conf, tool]
                return (VARIANT_STR_DELIMETER.join(slot_values))

        except KeyError as e:
            return (None, f"Required slot '{str(e)}' not provided")


# def load_dataclass_single(clazz: type, obj_ref: Optional[str], proj_dir : str, project_fs : FS, loader, local_types):
#     if obj_ref is None:
#         return None

#     error_format = base.EErrorFormat.MSVC if logger.IsIde() else base.EErrorFormat.Pretty

#     if not base.is_loaded_from_file(clazz):
#         clazz = base.loaded_from_file(clazz)

#     obj_path = fs.path.join(proj_dir, obj_ref)

#     if not project_fs.exists(obj_path) or not project_fs.isfile(obj_path):
#         raise ProjectError(f"Unknown to locate file '{obj_path}'")

#     with project_fs.open(obj_path, 'r', encoding='utf-8') as obj_file:
#         obj_templ = loader.load_dataclass(clazz, obj_path, obj_file.read(), local_types, error_format=error_format)

#         if obj_templ is not None:
#             if not base.is_loaded_from_file(obj_templ):
#                 raise ProjectError(f"Unable to load class '{type(obj_templ)}' from file, missing attribute 'loadable_from_file'!")

#             if logger.IsVisible(logger.ELogLevel.Verbose):
#                 logger.Success(f"Loaded [{clazz.__name__}] '{obj_path}'")

#             obj_templ.set_loaded_from_file(obj_path)
#             return obj_templ
#         else:
#             raise NoTraceError()


def load_dataclass_list(clazz: type, obj_ref_list: Optional[List[str]], proj_dir : str, project_fs : FS, loader, local_types, file_cache:Optional[FileCache] = None):
    result = []

    error_format = base.EErrorFormat.MSVC if logger.IsIde() else base.EErrorFormat.Pretty

    if not base.is_loaded_from_file(clazz):
        clazz = base.loaded_from_file(clazz)

    if obj_ref_list is not None and len(obj_ref_list) > 0:

        for obj_ref in obj_ref_list:
            if os.path.dirname(obj_ref) == '':
                logger.Warning(f"File '{obj_ref}' included from the same directory as main project file. Placement into subfolder is advised.")

            obj_path = fs.path.join(proj_dir, obj_ref)

            if not project_fs.exists(obj_path) or not project_fs.isfile(obj_path):
                raise ProjectError(f"Unknown to locate file '{obj_path}'")

            if file_cache is not None:
                file_cache.add_file(obj_path)

            with project_fs.open(obj_path, 'r', encoding='utf-8') as obj_file:
                obj_templ = loader.load_dataclass(clazz, obj_path, obj_file.read(), local_types, error_format=error_format)

                if obj_templ is not None:
                    if not base.is_loaded_from_file(obj_templ):
                        raise ProjectError(f"Unable to load class '{type(obj_templ)}' from file, missing attribute 'loadable_from_file'!")

                    if logger.IsVisible(logger.ELogLevel.Verbose):
                        logger.Success(f"Loaded [{clazz.__name__}] '{obj_path}'")

                    obj_templ.set_loaded_from_file(obj_path)
                    result.append(obj_templ)
                else:
                    raise ProjectError(f"Unable to load {clazz} from file '{obj_path}'")

    return result


def load_bundled_rules(loader, local_types) -> List[Rule]:
    result = []
    for res_path in [ 'MsvcRules.yml', 'ClangRules.yml' ]:
        res_content = resources.files('zetsubou.data.rules').joinpath(res_path).read_text()
        obj_templ = loader.load_dataclass(Rule, res_path, res_content, local_types)

        if obj_templ is not None:
            if not base.is_loaded_from_file(obj_templ):
                raise ProjectError(f"Unable to load class '{type(obj_templ)}' from file, missing attribute 'loadable_from_file'!")

            if logger.IsVisible(logger.ELogLevel.Verbose):
                logger.Success(f"Loaded [Rule] '{res_path}'")

            obj_templ.set_loaded_from_file(res_path)
            result.append(obj_templ)
    return result


def unpack_targets_from_any(any_targets) -> List[str]:
    result : List[str] = []

    def process_any(data):
        tp = type(data)

        if base.is_clazz_dict(tp):
            for _, value in data.items():
                process_any(value)

        if base.is_clazz_list(tp):
            for value in data:
                process_any(value)

        if tp is str:
            result.append(data)

    process_any(any_targets)

    return result


def load_project_template(project_fs: FS, fs_root : str, filename: str, proj_file_content: str, *,
                          loader=yaml_loader.YamlDataclassLoader(), external_config:Optional[ExternalConfig]=None, file_cache:Optional[FileCache]=None) -> Optional[ProjectTemplate]:
    try:
        local_types = base.get_types_from_modules([__name__, 'zetsubou.project.model.target'])

        if file_cache is not None:
            file_cache.add_file(filename)

        proj_dir = os.path.dirname(filename)
        proj_templ: Project = loader.load_dataclass(Project, filename, proj_file_content, local_types)
        if proj_templ is None:
            return

        proj_templ.set_loaded_from_file(filename)

        def load_dataclasses(clazz: type, obj_ref_list: Optional[List[str]]):
            return load_dataclass_list(clazz, obj_ref_list, proj_dir, project_fs, loader, local_types, file_cache)

        target_file_list = unpack_targets_from_any(proj_templ.targets)
        targets = load_dataclasses(Target, target_file_list)

        proj = ProjectTemplate(
            project=proj_templ,
            profile=None,
            platforms=load_dataclasses(Platform, proj_templ.config.platforms),
            system_toolchains=[],
            platform_toolchains={},
            cli_tools=load_dataclasses(CommandlineTool, proj_templ.config.cli_tools),
            configurations=load_dataclasses(Configuration, proj_templ.config.configurations),
            rules=load_dataclasses(Rule, proj_templ.config.rules),
            targets=targets,
        )

        if proj.project.config.config_string != CONFIG_STRING_DEPRECATED:
            logger.Warning('Deprecated field: config_string')

        # Profile handling
        if external_config is not None and external_config.profile_file is not None:
            proj.profile = load_dataclasses(Profile, [ external_config.profile_file ])[0]
        else:
            proj.profile = load_dataclasses(Profile, [ proj.project.config.dev_profile ])[0]

        # Filter by config
        if proj.profile is not None and proj.profile.build_type is not None:
            def is_from_base(config:Configuration):
                return config.base_configuration == proj.profile.build_type

            proj.configurations = list(filter(is_from_base, proj.configurations))
            if len(proj.configurations) == 0:
                raise ProjectError(f"No configurations of base type '{proj.profile.build_type}' found!")
            else:
                proj.configurations = [ proj.configurations[0] ]

        proj.rules += load_bundled_rules(loader, local_types)

        return proj

    except NoTraceError:
        logger.CriticalError(f'Failed to load project \'{filename}\'')
        return None

    except base.DataclassLoadError as error:
        logger.Error(error)
        logger.CriticalError(f'Failed to load project \'{filename}\'')
        return None

    except ProjectError as error:
        logger.Error(error)
        logger.CriticalError(f'Failed to load project \'{filename}\'')
        return None

    except Exception as error:
        logger.Exception(error)
        logger.CriticalError(f'Failed to load project  \'{filename}\'')
        return None


def load_project_from_file(project_fs: FS, fs_root : str, filename: str, *, external_config:Optional[ExternalConfig]=None, file_cache:Optional[FileCache]=None) -> Optional[ProjectTemplate]:
    if not project_fs.exists(filename):
        logger.CriticalError(f"Unable to locate file '{filename}'")
        return None
    with project_fs.open(filename, 'r', encoding='utf-8') as proj_file:
        return load_project_template(project_fs, fs_root, filename, proj_file.read(), external_config=external_config, file_cache=file_cache)
