from argparse import ArgumentParser
import os
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext
from zetsubou.commands.execute_stage import execute_stage
from zetsubou.conan.dependencies import ConanDependencies
from zetsubou.project.model.config_string import VARIANT_STR_DELIMETER
from zetsubou.project.model.toolchain_profile import Windows_ToolchainProfile
from zetsubou.project.model.virtual_environment import generate_empty_environment
from zetsubou.utils import logger
from zetsubou.utils.error_codes import EErrorCode
from zetsubou.utils.yaml_tools import to_yaml
from zetsubou.conan.conan import check_conan_present, call_conan
from zetsubou.conan.to_conan import runtime_to_conan, toolchain_to_conan, platform_to_conan, config_base_to_conan
from zetsubou.conan.deployer import get_conan_deployer_path


CONAN_OUT_PATH = 'build/conan'
CONAN_DEPS_FILE = 'build/conan_deps.yml'


class Install(Command):
    @property
    def name(self):
        return 'install'

    @property
    def desc(self):
        return 'Setup virtual environment, install build dependencies.'

    @property
    def help(self):
        return self.desc

    def ParseArgs(self, arg_parser: ArgumentParser):
        pass

    def OnExecute(self, context: CommandContext):
        if (is_conanfile_fresh(context, context.project_template.project.conan.build_tools) and
            is_conanfile_fresh(context, context.project_template.project.conan.dependencies) and
            is_conanfile_fresh(context, CONAN_DEPS_FILE)):
            return

        context.project_fs.makedirs('build/venv', recreate=True)

        if context.project_template.project.conan is not None and check_conan_present():
            self.generate_conan_environment(context)
        else:
            generate_empty_environment(context.project_fs)

    def merge_generated_part_files(self, context:CommandContext, conan_deps:str):
        dep_matrix = {}

        if not context.project_fs.exists(CONAN_OUT_PATH):
            logger.Error(f"Conan path '{CONAN_OUT_PATH}' doesn't exist!")
            return

        for path in context.project_fs.walk.files(path=CONAN_OUT_PATH, filter=['*.part.yml']):
            dep_name = os.path.basename(path).rsplit('.')[0]

            config_string = (os.path.basename(os.path.dirname(path))).replace('.', VARIANT_STR_DELIMETER)
            if not context.config_matrix.has_variant(config_string):
                logger.Verbose(f"Conan dependency '{dep_name}' uses '*' fallback for all variants")
                config_string = '*'

            if dep_name not in dep_matrix:
                dep_matrix[dep_name] = [
                    f'target: {dep_name}\n'
                    'config:\n'
                    '  kind: IMPORTED_TARGET\n'
                    'filters:\n'
                ]

            dep_target = dep_matrix[dep_name]

            with context.project_fs.open(path, mode='r') as part_file:
                dep_target.append(f"  - filter:\n       config_string: '{config_string}'\n")
                dep_target.append(part_file.read())

            dep_matrix[dep_name] = dep_target

        # Merge targets configurations into one file
        out_ymls = []
        for dep_name, dep_content in dep_matrix.items():
            out_yml_path = f'{CONAN_OUT_PATH}/{dep_name}.yml'
            out_ymls.append(out_yml_path)

            with context.project_fs.open(out_yml_path, mode='w') as out_file:
                out_file.write(''.join(dep_content))

        # Merge targets into one file
        if len(out_ymls) > 0:

            with context.project_fs.open(CONAN_DEPS_FILE, mode='w') as out_file:
                conan_deps = ConanDependencies(conanfile=conan_deps, targets=out_ymls)
                out_file.write(to_yaml(conan_deps))

            context.cache_file(CONAN_DEPS_FILE)
            context.conan.yml_files = out_ymls

    def generate_conan_environment(self, context: CommandContext):
        conan_build_tools = context.project_template.project.conan.build_tools
        if conan_build_tools is not None:
            context.cache_file(conan_build_tools)
            conan_build_tools = context.to_out_path(conan_build_tools)
            conan_out_directory = context.to_out_path("build/venv")
            execute_stage(lambda: call_conan(['install', conan_build_tools, '-g=VirtualBuildEnv', f'-of={conan_out_directory}'], conan_out_directory),
                        'Conan build tools installed',
                        EErrorCode.UNABLE_TO_INSTALL_CONAN_BUILD_TOOLS)

            context.resolve_venv()

        conan_deps = context.project_template.project.conan.dependencies
        if conan_deps is None:
            return

        context.cache_file(conan_deps)
        conan_deps = context.to_out_path(conan_deps)

        for config_variant in context.config_matrix.variants:
            logger.Verbose(f"Installing configuration '{config_variant.config_string}'")

            plat_name = config_variant.get_slot('platform')
            platform = context.project_template.find_platform(plat_name)
            toolchain = context.project_template.find_toolchain(plat_name, config_variant.get_slot('toolchain'))
            config = context.project_template.find_config(config_variant.get_slot('configuration'))

            conan_settings = []
            conan_settings.extend(platform_to_conan(context, platform))
            conan_settings.extend(toolchain_to_conan(context, toolchain))
            conan_settings.extend(config_base_to_conan(context, config))

            if isinstance(toolchain.profile, Windows_ToolchainProfile):
                conan_settings.extend(runtime_to_conan(config, toolchain))

            conan_config_out_path = f'{CONAN_OUT_PATH}/{config_variant.config_string.replace(VARIANT_STR_DELIMETER, ".")}'
            context.project_fs.makedirs(conan_config_out_path, recreate=True)

            conan_call_args = [
                'install', conan_deps, f'--build={context.project_template.project.conan.build}',
                '--deployer', get_conan_deployer_path(),
                f'-of={conan_config_out_path}',
            ]

            if context.project_template.project.conan.profile is not None:
                profile_path = context.to_out_path(context.project_template.project.conan.profile)
                conan_call_args += [
                    f'-pr:h={profile_path}'
                ]

            # pylint: disable=cell-var-from-loop
            execute_stage(lambda: call_conan(conan_call_args + conan_settings,
                        context.to_out_path(conan_config_out_path),
                        context.fs_venv),
                        f"Conan configuration '{config_variant.config_string}' installed",
                        EErrorCode.UNABLE_TO_INSTALL_CONAN_DEPENDENCIES)

        self.merge_generated_part_files(context, conan_deps)


def is_conanfile_fresh(context:CommandContext, filename:str):
    if filename == '' or filename is None:
        return True
    return context.file_cache.is_fresh(filename)
