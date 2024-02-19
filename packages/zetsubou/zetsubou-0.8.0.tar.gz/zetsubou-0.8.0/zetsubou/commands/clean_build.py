from argparse import ArgumentParser
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext
from zetsubou.utils import logger
from zetsubou.utils.error_codes import EErrorCode, ReturnErrorcode


class CleanBuild(Command):
    @property
    def name(self):
        return 'clean_build'

    @property
    def desc(self):
        return 'Removes built binaries.'

    @property
    def help(self):
        return self.desc

    def ParseArgs(self, arg_parser: ArgumentParser):
        pass

    @property
    def needs_project_loaded(self):
        return False

    def OnExecute(self, context: CommandContext):
        captured_exception = None
        dirs = ['build/bin', 'build/lib', 'build/obj']
        for dir in dirs:
            try:
                logger.Info(f"Removing built binaries from '{dir}' ...")
                if context.project_fs.exists(dir):
                    context.project_fs.removetree(dir)

            except Exception as err:
                logger.Error(f"Failed to remove '{dir}'")
                captured_exception = err

        if captured_exception is not None:
            raise ReturnErrorcode(EErrorCode.UNABLE_TO_CLEAN) from captured_exception
