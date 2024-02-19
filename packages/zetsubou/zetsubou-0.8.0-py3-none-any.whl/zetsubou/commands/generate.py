from argparse import ArgumentParser
import os
from fs.base import FS
from fs.copy import copy_fs
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext, Fastbuild
from zetsubou.commands.execute_stage import execute_stage
from zetsubou.commands.install import CONAN_DEPS_FILE, Install
from zetsubou.conan.dependencies import ConanDependencies
from zetsubou.fastbuild.fastbuild_emit import FastbuildEmitter
from zetsubou.project.model.target import Target
from zetsubou.project.model.virtual_environment import VirtualEnvironment
from zetsubou.project.runtime.emit import EmitContext, emit_project
from zetsubou.project.runtime.project_loader import load_dataclass_list
from zetsubou.project.runtime.resolve import ResolveContext, resolve_target_variants
from zetsubou.project.runtime.validation import ValidationContext, validate_targets, validate_cli_tools

from zetsubou.utils import logger
from zetsubou.utils.error_codes import EErrorCode
from zetsubou.utils.subprocess import call_process_venv
from zetsubou.utils.yaml_loader import YamlDataclassLoader as YAMLLoader
import bentoudev.dataclass.base as base

from fs import open_fs as fs_create

def commit_to_filesystem(project_fs : FS, mem_fs : FS, fs_root : str):
    copy_fs(mem_fs, project_fs)
    return True


def check_fastbuild_present(venv : VirtualEnvironment):
    out, err = call_process_venv(['fbuild', '-version'], venv, capture=True, realtime=False)
    if err is not None:
        logger.CriticalError('FASTbuild is missing, unable to proceed')
        return False

    logger.Success("FASTbuild present")
    logger.Verbose(out)
    return True


def call_fbuild_projects(fs_root : dir, bff_dir : str, bff_file : str, venv_obj : VirtualEnvironment):
    bff_dir = os.path.join(fs_root, bff_dir)
    bff_file = os.path.join(fs_root, bff_dir, bff_file)

    verbose = logger.IsVisible(logger.ELogLevel.Verbose)

    assert os.path.isfile(bff_file)
    assert not os.path.isfile(bff_dir)

    out, err = call_process_venv(['fbuild', '-config', bff_file], venv_obj, capture = not verbose, realtime = verbose, cwd = bff_dir)
    if err is not None:

        if not verbose:
            logger.Error(out)

        logger.CriticalError(f"FASTbuild returned error '{err}'")
        return False

    if verbose:
        print('')
    return True


def call_fbuild_solution(fs_root : dir, bff_dir : str, bff_file : str, project_name : str, venv_obj : VirtualEnvironment):
    bff_dir = os.path.join(fs_root, bff_dir)
    bff_file = os.path.join(fs_root, bff_dir, bff_file)

    verbose = logger.IsVisible(logger.ELogLevel.Verbose)
    if verbose:
        print('')

    assert os.path.isfile(bff_file)
    assert not os.path.isfile(bff_dir)

    out, err = call_process_venv(['fbuild', '-config', bff_file, project_name, '-ide'], venv_obj, capture=not verbose, realtime=verbose, cwd=bff_dir)
    if err is not None:

        if not verbose:
            logger.Error(out)

        logger.CriticalError(f"FASTbuild returned error '{err}'")
        return False

    if verbose:
        print('')
    return True


def load_dependencies(context: CommandContext):
    loader = YAMLLoader()
    local_types = base.get_types_from_modules([__name__, 'zetsubou.project.model.target'])
    dep_targets = []

    conan_deps = context.project_template.project.conan.dependencies
    if conan_deps is None:
        return True

    conan_deps = context.to_out_path(conan_deps)

    def load_deps():
        path = CONAN_DEPS_FILE

        # Merge files, only parts from deployer exist
        if not context.project_fs.exists(path):
            Command.get_command_instance(Install).merge_generated_part_files(context, conan_deps)
            return True

        # Load merged yaml
        with context.project_fs.open(path, 'r', encoding='utf-8') as obj_file:
            context.cache_file(path)

            obj_templ : ConanDependencies = loader.load_dataclass(ConanDependencies, path, obj_file.read(), local_types)

            if obj_templ is None:
                return False

            context.conan.yml_files = obj_templ.targets

        return True

    if len(context.conan.yml_files) == 0:
        if not load_deps():
            return False

    dep_targets = context.conan.yml_files

    if len(dep_targets) != 0:
        context.conan.dependencies = load_dataclass_list(Target, dep_targets, '', context.project_fs, loader, local_types, context.file_cache)

    return True


def validate_project(context: CommandContext):
    vctx = ValidationContext()
    vctx.error_format = base.EErrorFormat.MSVC if context.command_args.ide else base.EErrorFormat.Pretty

    validate_targets(vctx, context.project_template.targets + context.conan.dependencies)
    validate_cli_tools(vctx, context.project_template.targets, context.project_template.cli_tools)

    return True


class Generate(Command):
    @property
    def name(self):
        return 'gen'

    @property
    def desc(self):
        return 'Discover toolchains, Resolve dependencies, Generate project files.'

    @property
    def help(self):
        return self.desc

    def ParseArgs(self, arg_parser: ArgumentParser):
        pass

    def OnExecute(self, context: CommandContext):
        # venv could have been generated by conan install or already present in fs
        context.resolve_venv()

        # discover dependencies
        execute_stage(lambda: load_dependencies(context),
                    'Conan dependencies loaded',
                    EErrorCode.UNABLE_TO_LOAD_DEPENDENCIES)

        # Validate target references
        execute_stage(lambda: validate_project(context),
                    'Targets validated',
                    EErrorCode.UNABLE_TO_VALIDATE_TARGETS)

        resolve_context = ResolveContext.from_base(context)
        resolve_context.project=context.project_template

        if len(context.conan.dependencies) > 0:
            # create variants of conan deps per configuration
            context.conan.resolved_targets = execute_stage(lambda: resolve_target_variants(resolve_context, context.config_matrix, context.conan.dependencies),
                                        'Resolved Conan target variants',
                                        EErrorCode.UNABLE_TO_RESOLVE_VARIANTS)

        # create variants of targets per configuration
        context.resolved_targets = execute_stage(lambda: resolve_target_variants(resolve_context, context.config_matrix, context.project_template.targets),
                                    'Resolved target variants dependencies',
                                    EErrorCode.UNABLE_TO_RESOLVE_VARIANTS)

        emit_context = EmitContext.from_base(context)
        emit_context.project_template=context.project_template
        emit_context.resolved_targets=context.resolved_targets
        emit_context.config_matrix=context.config_matrix
        emit_context.conan=context.conan
        emit_context.mem_fs=fs_create('mem://', default_protocol='mem')

        # fill objects for csproj and sln from target variants
        # save to virtual filesystem
        emit_result_tuple = execute_stage(lambda: emit_project(
                                    emit_context,
                                    emitter=FastbuildEmitter()),
                                    'Project data generated',
                                    EErrorCode.UNABLE_TO_EMIT_PROJECT)

        context.fastbuild = Fastbuild(*emit_result_tuple)

        # commit virtual filesystem to os
        if not context.command_args.dry:
            execute_stage(lambda: commit_to_filesystem(context.project_fs, context.fastbuild.emit_fs, context.fastbuild.bff_dir),
                'Files commited to filesystem',
                EErrorCode.UNABLE_TO_COMMIT_FS)

            if check_fastbuild_present(context.fs_venv):
                execute_stage(lambda: call_fbuild_projects(context.fs_root, context.fastbuild.bff_dir, context.fastbuild.bff_file,
                    context.fs_venv),
                    'FASTbuild projects generated',
                    EErrorCode.UNABLE_TO_CREATE_VS_PROJECTS)

                execute_stage(lambda: call_fbuild_solution(context.fs_root, context.fastbuild.bff_dir, context.fastbuild.bff_file,
                    context.project_template.project.project, context.fs_venv),
                    'FASTbuild solution generated',
                    EErrorCode.UNABLE_TO_CREATE_VS_SOLUTION)
