from typing import List
from dataclasses import dataclass, field

from zetsubou.project.model.configuration_enums import EBaseConfiguration
from zetsubou.project.model.filter import TargetFilter
from zetsubou.project.model.target import TargetData
from bentoudev.dataclass.base import loaded_from_file


@dataclass
class ConfigurationData(TargetData):
    filter: TargetFilter = field(default_factory=TargetFilter)


@dataclass
@loaded_from_file
class Configuration(TargetData):
    configuration: str = None
    base_configuration: EBaseConfiguration = None
    filters: List[ConfigurationData] = field(default_factory=list)
