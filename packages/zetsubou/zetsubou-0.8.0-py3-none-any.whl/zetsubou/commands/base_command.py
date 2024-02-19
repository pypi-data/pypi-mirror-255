from argparse import ArgumentParser
from typing import List, Optional
import os

import bentoudev.dataclass.base as base

from zetsubou.commands.execute_stage import execute_stage
from zetsubou.commands.command_context import CommandContext
from zetsubou.project.model.config_string import EDefaultConfigSlots
from zetsubou.project.runtime.project_loader import ProjectTemplate, load_project_from_file, ExternalConfig
from zetsubou.project.config_matrix import ConfigMatrix, ConfigVariant, create_config_matrix
from zetsubou.project.runtime.validation import ValidationContext, validate_profile
from zetsubou.system import discover_toolchains, tools
from zetsubou.utils import logger
from zetsubou.utils.common import fix_path
from zetsubou.utils.error_codes import EErrorCode


class Command:
    _commands : List['Command'] = []

    @staticmethod
    def is_initialized() -> bool:
        return len(Command._commands) > 0

    @staticmethod
    def initialize_command_instances(cmds : List['Command']):
        Command._commands = cmds

    @staticmethod
    def get_commands():
        return Command._commands

    @staticmethod
    def get_command_by_name(name:str):
        for c in Command._commands:
            if c.name == name:
                return c
        raise ValueError(f"Cannot find command with name '{name}'!")

    @staticmethod
    def get_command_instance(t):
        for c in Command._commands:
            if isinstance(c, t):
                return c
        raise ValueError(f"Cannot find instance of command '{t.__name__}'!")

    # User readable name
    @property
    def name(self):
        raise NotImplementedError()

    # Short information, displayed for --help
    @property
    def help(self):
        raise NotImplementedError()

    # Detailed information, displayed for COMMAND --help
    @property
    def desc(self):
        raise NotImplementedError()

    # Will require positional PROJECT argument
    # Will automatically load project before executing this command
    @property
    def needs_project_loaded(self):
        return True

    # Parses additional arguments that may be provided for this command
    def ParseArgs(self, arg_parser : ArgumentParser):
        raise NotImplementedError()

    def Execute(self, context : CommandContext):
        if self.needs_project_loaded:
            self._load_project(context)

        logger.Command(self.name)
        self.OnExecute(context)

    def OnExecute(self, context : CommandContext):
        raise NotImplementedError()

    def _load_project(self, context : CommandContext):
        if context.project_template is None:

            logger.Command('load_project')

            if not context.file_cache.load(context.project_fs):
                logger.Info('Stale cache, will regenerate')

            external_config = ExternalConfig()

            # handle platform from external file
            if hasattr(context.command_args, 'profile') and context.command_args.profile is not None:
                profile_file = os.path.relpath(context.command_args.profile, context.fs_root) if os.path.isabs(context.command_args.profile) else context.command_args.profile
                external_config.profile_file = fix_path(profile_file)

                logger.Info(f"Using profile from external file '{external_config.profile_file}'")

            # load and process project
            context.project_template = execute_stage(lambda: load_project_from_file(
                                        context.project_fs,
                                        context.fs_root,
                                        context.project_file,
                                        external_config=external_config,
                                        file_cache=context.file_cache),
                                        'Project loaded',
                                        EErrorCode.UNABLE_TO_LOAD_PROJECT)

            context.project_template.platforms = tools.filter_platforms_by_host(
                context.host_system,
                context.host_arch,
                context.project_template.platforms)

            # validate platforms
            vctx = ValidationContext()
            vctx.error_format = base.EErrorFormat.MSVC if context.command_args.ide else base.EErrorFormat.Pretty
            validate_profile(vctx, context.project_template.profile)

            # discovering and filtering of toolchains
            context.project_template.platform_toolchains, context.project_template.system_toolchains = execute_stage(
                lambda: discover_toolchains.discover_toolchain_list(context),
                'Toolchains discovered',
                EErrorCode.UNABLE_TO_DISCOVER_TOOLCHAIN)

            # create matrix of all options and their possible values
            context.config_matrix = execute_stage(lambda: resolve_config_matrix(context.project_template),
                                      'Config matrix created',
                                      EErrorCode.UNABLE_TO_CREATE_CONFIGURATIONS)


def resolve_config_matrix(project_template:ProjectTemplate) -> Optional[ConfigMatrix]:
    # Full config matrix, contains incorrect entries (toolchain/platform mismatched)
    config_matrix = create_config_matrix(project_template.slot_values())

    def filter_tool_by_plat(variant: ConfigVariant):
        toolchain = project_template.find_toolchain(
            variant.get_slot(EDefaultConfigSlots.platform.name),
            variant.get_slot(EDefaultConfigSlots.toolchain.name))

        return toolchain is not None

    # Filter out incorrect variants
    config_matrix.variants = list(filter(filter_tool_by_plat, config_matrix.variants))
    if len(config_matrix.variants) == 0:
        return None

    return config_matrix
