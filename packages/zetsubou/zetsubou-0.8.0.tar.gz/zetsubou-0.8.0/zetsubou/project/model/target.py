from typing import List, Optional
from dataclasses import dataclass, field

from zetsubou.project.model.filter import TargetFilter
from zetsubou.project.model.kind import ETargetKind
from bentoudev.dataclass.base import inline_loader, track_source, loaded_from_file


@dataclass
class Dependencies:
    interface: Optional[List['zetsubou.project.model.target.TargetReference']] = field(default_factory=list) # noqa: F821
    public: Optional[List['zetsubou.project.model.target.TargetReference']] = field(default_factory=list)    # noqa: F821
    private: Optional[List['zetsubou.project.model.target.TargetReference']] = field(default_factory=list)   # noqa: F821


@dataclass
class Source:
    paths: List[str] = field(default_factory=list)
    patterns: Optional[List[str]] = field(default_factory=list)


@dataclass
class PropertyList:
    interface: Optional[List[str]] = field(default_factory=list)
    public: Optional[List[str]] = field(default_factory=list)
    private: Optional[List[str]] = field(default_factory=list)


@dataclass
class PathList(PropertyList):
    pass


@dataclass
class TargetData:
    dependencies: Optional[Dependencies] = field(default=None)
    source: Optional[Source] = field(default=None)
    source_exclude: Optional[Source] = field(default=None)
    includes: Optional[PathList] = field(default=None)
    system_includes: Optional[PathList] = field(default=None)
    defines: Optional[PropertyList] = field(default=None)
    compiler_flags: Optional[PropertyList] = field(default=None)
    linker_flags: Optional[PropertyList] = field(default=None)
    librarian_flags: Optional[PropertyList] = field(default=None)
    linker_paths: Optional[PathList] = field(default=None)
    link_libraries: Optional[PropertyList] = field(default=None)
    distribute_files: Optional[Source] = field(default=None)
    build_require: Optional[List['zetsubou.project.model.target.TargetReference']] = field(default_factory=list) # noqa: F821


@dataclass
class TargetFilterData(TargetData):
    filter: TargetFilter = field(default_factory=TargetFilter)


@dataclass
class TargetConfig:
    kind: ETargetKind
    compiler: Optional[str] = None


@dataclass
@loaded_from_file
@track_source
class Target(TargetData):
    target: str = ''
    config: TargetConfig = None
    filters: Optional[List[TargetFilterData]] = field(default_factory=list)


@inline_loader(source_type=str, field_name='name')
@track_source
@dataclass
class TargetReference:
    name: str
    target: Target = None

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, TargetReference):
            return self.name == other.name
        return False

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)


def find_target(targets: List[Target], name: str) -> Optional[Target]:
    for target in targets:
        if target.target == name:
            return target
    return None
