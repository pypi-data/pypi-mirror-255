from typing import List, Optional, Any
from dataclasses import dataclass, field

from bentoudev.dataclass.base import loaded_from_file, track_source

CONFIG_STRING_DEPRECATED = 'DEPRECATED'

@dataclass
@track_source
class ProjectConfig:
    verbose_build: Optional[bool] = False
    dev_profile: str = ''
    platforms: List[str] = field(default_factory=list)
    configurations: List[str] = field(default_factory=list)
    cli_tools: Optional[List[str]] = field(default_factory=list)
    # slots: Optional[List[str]] = field(default_factory=list)
    rules: Optional[List[str]] = field(default_factory=list)
    config_string: Optional[str] = CONFIG_STRING_DEPRECATED
    venv: Optional[str] = ''


@dataclass
class Option:
    name: str
    values: List[str]


@dataclass
class Conan:
    build_tools: Optional[str] = None
    dependencies: Optional[str] = None
    build: Optional[str] = 'missing'
    profile: Optional[str] = None


@loaded_from_file
@dataclass
class Project:
    project: str
    config: ProjectConfig
    targets: Any
    conan: Optional[Conan] = None
    options: Optional[List[Option]] = field(default_factory=list)
