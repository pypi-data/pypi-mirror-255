from typing import List


class DataclassLoader:
    def load_dataclass(self, clazz: type, filename: str, file_content: str, ext_types: List[type]):
        raise NotImplementedError
