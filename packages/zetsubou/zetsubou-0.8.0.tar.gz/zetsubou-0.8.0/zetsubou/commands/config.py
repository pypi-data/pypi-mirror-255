from argparse import ArgumentParser
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext
from zetsubou.commands.install import Install
from zetsubou.commands.generate import Generate


class Config(Command):
    def install(self):
        return Command.get_command_instance(Install)

    def gen(self):
        return Command.get_command_instance(Generate)

    @property
    def name(self):
        return 'config'

    @property
    def desc(self):
        return f'{self.install().desc} {self.gen().desc}'

    @property
    def help(self):
        return 'Calls [install] and [gen].'

    def ParseArgs(self, arg_parser: ArgumentParser):
        pass

    @property
    def needs_project_loaded(self):
        return True

    def OnExecute(self, context: CommandContext):
        self.install().OnExecute(context)
        self.gen().OnExecute(context)
