from argparse import ArgumentParser
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext
from zetsubou.utils import logger
from zetsubou.utils.error_codes import EErrorCode, ReturnErrorcode
from fs.errors import ResourceNotFound


class Clean(Command):
    @property
    def name(self):
        return 'clean'

    @property
    def desc(self):
        return 'Removes build folder and solution files.'

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
            logger.Info("Removing 'build' ...")
            if context.project_fs.exists('build'):
                context.project_fs.removetree('build')

        except ResourceNotFound as err:
            pass

        except Exception as err:
            logger.Error(f"Failed to remove 'build'")
            logger.Exception(err)
            raise ReturnErrorcode(EErrorCode.UNABLE_TO_CLEAN) from err

        # --

        try:
            logger.Info("Removing '*.sln' ...")
            for path in context.project_fs.walk(path='.', filter=['*.sln']):
                for file in path.files:
                    context.project_fs.remove(file.name)

        except ResourceNotFound as err:
            pass

        except Exception as err:
            logger.Error("Failed to remove '*.sln'")
            logger.Exception(err)
            raise ReturnErrorcode(EErrorCode.UNABLE_TO_CLEAN) from err
