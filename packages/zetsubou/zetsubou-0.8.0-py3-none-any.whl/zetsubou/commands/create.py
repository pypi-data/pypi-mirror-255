from argparse import ArgumentParser
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext
from zetsubou.commands.execute_stage import execute_stage
from zetsubou.utils import logger

import fs, os
from fs.copy import copy_fs
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from zetsubou.utils.error_codes import EErrorCode


def emit_project_template(templ_dir:str, data_fs:FS, out_fs:FS):
    if not data_fs.exists(templ_dir) or not data_fs.isdir(templ_dir):
        return None

    for itr in data_fs.walk(templ_dir):
        rel_path = fs.path.relativefrom(templ_dir, itr.path)
        out_fs.makedirs(rel_path, recreate=True)
        for file in itr.files:
            rel_file = fs.path.join(rel_path, file.name)
            out_file_handle = out_fs.openbin(rel_file, mode='w')
            data_fs.download(fs.path.join(itr.path, file.name), out_file_handle)

    return out_fs


class Create(Command):
    @property
    def name(self):
        return 'create'

    @property
    def desc(self):
        return 'Creates new project from selected template.'

    @property
    def help(self):
        return self.desc

    def ParseArgs(self, arg_parser: ArgumentParser):
        pass

    @property
    def needs_project_loaded(self):
        return False

    def OnExecute(self, context: CommandContext):
        try:
            project_template = 'data/default_project'

            out_fs = execute_stage(lambda: emit_project_template(project_template, data_fs=OSFS(os.getcwd()), out_fs=MemoryFS()),
                'Created new project',
                EErrorCode.UNABLE_TO_COMMIT_FS)

            if out_fs is not None and not context.command_args.dry:
                copy_fs(out_fs, context.project_fs)

        except Exception as exc:
            logger.Exception(exc)
            raise
