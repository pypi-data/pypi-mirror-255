from typing import Optional, List
from dataclasses import dataclass

from zetsubou.project.model.kind import ETargetKind
from zetsubou.project.model.runtime_library import ERuntimeLibrary
from zetsubou.project.model.configuration_enums import EBaseConfiguration


@dataclass
class TargetFilter():
    config_string: str = '*'
    kind: Optional[List[ETargetKind]] = None
    runtime_library: Optional[List[ERuntimeLibrary]] = None
    base_configuration: Optional[List[EBaseConfiguration]] = None
