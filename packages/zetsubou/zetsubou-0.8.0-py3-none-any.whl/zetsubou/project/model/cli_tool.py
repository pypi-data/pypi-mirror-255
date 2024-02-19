from dataclasses import dataclass, field
from typing import List, Optional
from zetsubou.project.model.virtual_environment import VirtualEnvironment
from zetsubou.utils.subprocess import call_process_venv


@dataclass
class CommandlineTool:
    name: str
    executable: str

    """
    Supports:
        %1 - Input file(s) as provided via ExecInput argument.
        %2 - Output file as provided by output_file argument.
        %3 - Output dir as provided by output_dir argument.
    """
    options: List[str]
    output_file: str
    output_dir: str

    _exec_fullpath: Optional[str] = field(init=False, repr=False, default=None)

    # Can only be called after tool fullpath was resolved successfully
    @property
    def executable_fullpath(self):
        assert self._exec_fullpath is not None
        return self._exec_fullpath

    # Finds executable fullpath in virtual environment
    def resolve(self, venv:VirtualEnvironment) -> bool:
        # Downside is that we kinda assumed venv would be a thing, but it is not - fastbuild doesn't want it...
        out, err = call_process_venv(['where', self.executable], venv, capture=True, realtime=False)

        if err is not None:
            return False

        self._exec_fullpath = out.strip()
        return True
