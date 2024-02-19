from typing import List
from zetsubou.commands.base_command import Command
from zetsubou.commands.clean import Clean
from zetsubou.commands.generate import Generate
from zetsubou.commands.regen import Regen
from zetsubou.commands.install import Install
from zetsubou.commands.create import Create
from zetsubou.commands.build import Build
from zetsubou.commands.clean_build import CleanBuild
from zetsubou.commands.config import Config


def get_all_commands() -> List[Command]:
    if not Command.is_initialized():
        Command.initialize_command_instances([
            Clean(),
            Config(),
            Install(),
            Generate(),
            Regen(),
            Create(),
            Build(),
            CleanBuild(),
        ])

    return Command.get_commands()
