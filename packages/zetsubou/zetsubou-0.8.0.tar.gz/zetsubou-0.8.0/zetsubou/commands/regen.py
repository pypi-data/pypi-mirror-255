from argparse import ArgumentParser
from zetsubou.commands.base_command import Command
from zetsubou.commands.command_context import CommandContext
from zetsubou.commands.clean import Clean
from zetsubou.commands.install import Install
from zetsubou.commands.generate import Generate


class Regen(Command):
    def clean(self):
        return Command.get_command_instance(Clean)

    def install(self):
        return Command.get_command_instance(Install)

    def gen(self):
        return Command.get_command_instance(Generate)

    @property
    def name(self):
        return 'regen'

    @property
    def desc(self):
        return f'{self.clean().desc} {self.install().desc} {self.gen().desc}'

    @property
    def help(self):
        return 'Calls [clean] and then [install] and [gen].'

    def ParseArgs(self, arg_parser: ArgumentParser):
        self.clean().ParseArgs(arg_parser)
        self.install().ParseArgs(arg_parser)
        self.gen().ParseArgs(arg_parser)

    @property
    def needs_project_loaded(self):
        return True

    def OnExecute(self, context: CommandContext):
        self.clean().OnExecute(context)
        self.install().OnExecute(context)
        self.gen().OnExecute(context)
