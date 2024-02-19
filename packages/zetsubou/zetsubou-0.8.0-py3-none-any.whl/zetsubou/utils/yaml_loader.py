from typing import List

import bentoudev.dataclass.yaml_loader as yaml
import bentoudev.dataclass.base as base

from zetsubou.utils import logger
from zetsubou.utils.dataclass_loader import DataclassLoader

class YamlDataclassLoader(DataclassLoader):
    def __init__(self):
        self.type_cache = yaml.default_type_loaders()

    def load_dataclass(self, clazz: type, filename: str, file_content: str, ext_types: List[type], *, error_format=base.EErrorFormat.Pretty):
        classname = clazz.__name__.lower()
        label = f"[{classname}] {filename}"
        logger.Loading(classname, filename)

        try:
            return yaml.load_yaml_dataclass(clazz, label, file_content, type_cache=self.type_cache, ext_types=ext_types, always_track_source=True, error_format=error_format)

        except base.DataclassLoadError as error:
            logger.Error(error)
            logger.CriticalError(f'Failed to load {classname} \'{filename}\'')
            return None
