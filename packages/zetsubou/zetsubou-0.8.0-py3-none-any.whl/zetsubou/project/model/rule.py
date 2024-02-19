from typing import List
from dataclasses import dataclass, field
from zetsubou.project.model.filter import TargetFilter
from zetsubou.project.model.target import TargetData
from bentoudev.dataclass.base import loaded_from_file


@dataclass
class RuleData(TargetData):
    filter: TargetFilter = field(default_factory=TargetFilter)


@dataclass
@loaded_from_file
class Rule:
    rule: str
    filters: List[RuleData]
