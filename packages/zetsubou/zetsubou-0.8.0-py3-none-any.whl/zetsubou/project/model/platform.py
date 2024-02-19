from typing import List, Optional
from dataclasses import dataclass, field
from dataclasses import dataclass

from zetsubou.project.model.platform_enums import ESystem, EArch
from zetsubou.project.model.filter import TargetFilter
from zetsubou.project.model.target import TargetData
from bentoudev.dataclass.base import loaded_from_file


@dataclass
class PlatformData(TargetData):
    filter: TargetFilter = field(default_factory=TargetFilter)


@dataclass
@loaded_from_file
class Platform(TargetData):
    platform: str = None
    host_system: ESystem = None
    host_arch: EArch = None
    target_arch: EArch = None
    filters: Optional[List[PlatformData]] = field(default_factory=list)
