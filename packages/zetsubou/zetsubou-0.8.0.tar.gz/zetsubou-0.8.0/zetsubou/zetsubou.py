from __future__ import absolute_import
import os
import time
from typing import Optional, List
from sys import argv as sys_argv

from fs.osfs import OSFS
from zetsubou.commands.base_command import CommandContext, Command
from zetsubou.commands.command_registry import get_all_commands

from zetsubou.logo import print_logo
from zetsubou.project.runtime.project_loader import ProjectError
from zetsubou.utils import logger
from zetsubou.utils.cmd_arguments import parse_arguments
from zetsubou.utils.common import fix_path
from zetsubou.utils.error import CompilationError
from zetsubou.utils.error_codes import EErrorCode, ReturnErrorcode
from zetsubou.system.tools import get_host_arch, get_host_system
from zetsubou._version import get_author_desc


def main(argv: List[str] = sys_argv[1:]) -> int:
    desc = f'FASTbuild project generator for the helpless\n{get_author_desc()}'
    progname = 'zetsubou'
    start_time = time.time()
    logger.Initialize()

    try:
        # populate command list
        command_registry = get_all_commands()

        # parse cmd arguments
        zet_args = parse_arguments(argv, progname, desc, command_registry)

        if not zet_args.nologo and not zet_args.ide and not zet_args.silent:
            print_logo(desc)

        if zet_args.ide:
            logger.SetIde(True)

        if zet_args.silent:
            logger.SetLogLevel(logger.ELogLevel.Silent)
        elif zet_args.verbose:
            logger.SetLogLevel(logger.ELogLevel.Verbose)

        has_project_context = hasattr(zet_args, 'project')

        fs_root = os.path.dirname(os.path.normpath(os.path.join(os.getcwd(), zet_args.project))) if has_project_context else os.getcwd()
        project_file = os.path.basename(zet_args.project) if has_project_context else None

        command_context = CommandContext(
            host_arch = get_host_arch(),
            host_system = get_host_system(),
            fs_root = fix_path(fs_root),
            command_args = zet_args,
            project_file = project_file,
            project_fs = OSFS(fs_root)
        )

        logger.Info(f"Current working directory - '{os.getcwd()}'")
        logger.Info(f"Project working directory - '{fs_root}'")

        cmd = Command.get_command_by_name(zet_args.command)
        cmd.Execute(command_context)

        command_context.file_cache.save()

        end_time = time.time()

        if not zet_args.silent:
            print(f'\nFinished in {end_time - start_time:.2f} sec')

        return 0

    except ReturnErrorcode as errcode:
        logger.ReturnCode(errcode.error_code)
        return errcode.error_code.value

    except ProjectError as proj_error:
        logger.Error(proj_error)
        logger.ReturnCode(EErrorCode.UNKNOWN_ERROR)
        return EErrorCode.UNKNOWN_ERROR.value

    except CompilationError:
        logger.ReturnCode(EErrorCode.COMPILATION_FAILED)
        return EErrorCode.COMPILATION_FAILED.value

    except Exception as error:
        logger.Exception(error)
        return EErrorCode.UNKNOWN_ERROR.value
