import os
from dataclasses import dataclass, field
from typing import List, Optional, Any
from fs.base import FS

from zetsubou.commands.execute_stage import execute_stage
from zetsubou.utils import logger
from zetsubou.utils.common import fix_path
from zetsubou.project.config_matrix import ConfigMatrix
from zetsubou.project.base_context import BaseContext
from zetsubou.project.model.target import Target
from zetsubou.project.model.virtual_environment import VirtualEnvironment, resolve_venv
from zetsubou.project.runtime.resolve import ResolvedTarget
from zetsubou.project.runtime.project_loader import ProjectTemplate
from zetsubou.utils.error_codes import EErrorCode
from zetsubou.utils.file_cache import FileCache

@dataclass
class Fastbuild:
    emit_fs : FS
    bff_dir : str
    bff_file : str


@dataclass
class Conan:
    yml_files: List[str] = field(default_factory=list)
    dependencies: List[Target] = field(default_factory=list)
    resolved_targets: List[ResolvedTarget] = field(default_factory=list)


@dataclass
class CommandContext(BaseContext):
    command_args: Any = None

    project_template: Optional[ProjectTemplate] = None
    # toolchains: List[ToolchainDefinition] = field(default_factory=list)
    config_matrix: Optional[ConfigMatrix] = None
    resolved_targets: List[ResolvedTarget] = field(default_factory=list)
    fastbuild: Optional[Fastbuild] = None
    conan: Conan = field(default_factory=Conan)
    file_cache: FileCache = field(default_factory=FileCache)

    def cache_file(self, filename:str):
        if self.file_cache:
            self.file_cache.add_file(filename)

    def to_out_path(self, path : str):
        return fix_path(os.path.join(self.fs_root, path))

    def resolve_cli_tools(self):
        for cli_tool in self.project_template.cli_tools:
            if not cli_tool.resolve(self.fs_venv):
                logger.Error(f"Unable to resolve fullpath to '{cli_tool.executable}'. Might be missing from venv or PATH.")
                return False
        return True

    def resolve_venv(self):
        if self.fs_venv is None:
            venv_obj : VirtualEnvironment = execute_stage(lambda: resolve_venv(self.project_fs, self.project_template.project, self.fs_root),
                                        'Virtual environemnt found',
                                        EErrorCode.UNABLE_TO_FIND_VENV)

            logger.Info(f"Virtual environement - '{venv_obj.activate}'")
            self.fs_venv = VirtualEnvironment(self.to_out_path(venv_obj.activate), self.to_out_path(venv_obj.deactivate))

            # resolve fullpaths to cli tools
            execute_stage(self.resolve_cli_tools,
                          'Commandline tools found',
                          EErrorCode.UNABLE_TO_RESOLVE_CLI_TOOLS_FULLPATH)
