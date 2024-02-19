from typing import List
from dataclasses import dataclass
from bentoudev.dataclass.base import loaded_from_file, track_source

@dataclass
@track_source
@loaded_from_file
class ConanDependencies():
    conanfile: str
    targets: List[str]
