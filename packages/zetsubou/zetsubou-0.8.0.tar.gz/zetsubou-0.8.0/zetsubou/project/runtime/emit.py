from typing import List, ClassVar
from dataclasses import dataclass, field
from enum import Enum

from fs.base import FS
from fs.path import combine as fs_combine
from fs.path import dirname as fs_dirname
from fs.path import basename as fs_basename

from zetsubou.project.base_context import BaseContext
from zetsubou.project.runtime.project_loader import ProjectTemplate
from zetsubou.project.runtime.resolve import ResolvedTarget
from zetsubou.project.config_matrix import ConfigMatrix
from zetsubou.commands.command_context import Conan


class EDefaultTargets(Enum):
    All = 0x1
    Update = 0x2


@dataclass
class EmitContext(BaseContext):
    project_template: ProjectTemplate = None
    resolved_targets: List[ResolvedTarget] = field(default_factory=list)
    config_matrix: ConfigMatrix = None
    conan: Conan = None
    mem_fs: FS = None
    ROOT_DIR: ClassVar[str] = "."

    @classmethod
    def from_base(cls, source : BaseContext):
        result = EmitContext()
        result.__dict__.update(source.__dict__)
        return result

    def write_file(self, rw_path: str, content: str):
        dirname = fs_dirname(rw_path)
        filename = fs_basename(rw_path)

        dirname = fs_combine(EmitContext.ROOT_DIR, dirname)

        with self.mem_fs.makedirs(dirname, recreate=True) as out_dir:
            with out_dir.open(filename, 'w') as out_file:
                out_file.write(content)


class Emitter:
    def emit_solution(self, context: EmitContext) -> str:
        raise NotImplementedError()

    def emit_target(self, context: EmitContext, target: ResolvedTarget):
        raise NotImplementedError()


def emit_project(context: EmitContext, emitter: Emitter):
    # emit target files
    for target in context.resolved_targets:
        emitter.emit_target(context, target)

    # emit main project file
    main_file = emitter.emit_solution(context)

    return (context.mem_fs, EmitContext.ROOT_DIR, main_file)
