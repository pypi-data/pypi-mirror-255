import argparse
from typing import List
from textwrap import dedent

from zetsubou._version import __version__, get_author_desc
from zetsubou.commands.base_command import Command


class SmartFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = dedent(text)
        return ''.join(indent + line for line in text.splitlines(True))


def parse_arguments(in_args:List[str], program_name: str, desc: str, command_registry : List[Command]):
    main_parser = argparse.ArgumentParser(prog=program_name, description=desc, formatter_class=SmartFormatter)

    main_parser.add_argument('--version', action='version', version=f'Zetsubou {__version__} - Copyright {get_author_desc()}')

    parent_parser = argparse.ArgumentParser(add_help=False)

    def add_global_options(parser):
        parser.add_argument('--nologo', action='store_true', default=False, help='skip printing of the logo')
        parser.add_argument('--ide', action='store_true', default=False, help='print messages in IDE friendly way')
        parser.add_argument('--dry', action='store_true', default=False, help='make no changes in filesystem')

        parser.add_argument('--profile', help='Constraints variant matrix to external profile')

        log_group = parser.add_mutually_exclusive_group()
        log_group.add_argument('--verbose', action='store_true', default=False, help='print more information during execution')
        log_group.add_argument('--silent', action='store_true', default=False, help='print only errors')

    add_global_options(parent_parser)

    subcommands = main_parser.add_subparsers(dest='command', metavar='COMMAND', required=True)

    for command in command_registry:
        sub_cmd = subcommands.add_parser(name=command.name, help=command.help, description=command.desc, parents=[parent_parser])
        if (command.needs_project_loaded):
            sub_cmd.add_argument('project', metavar='PROJECT', type=str, help='YAML file describing the project', default='project.yml')
        command.ParseArgs(sub_cmd)

    result = main_parser.parse_args(in_args)
    return result
