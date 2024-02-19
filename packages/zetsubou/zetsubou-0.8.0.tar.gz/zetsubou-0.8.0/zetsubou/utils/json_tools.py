import json, dataclasses
from enum import Enum

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, Enum):
            return o.name
        return super().default(o)

def to_json(obj):
    return json.dumps(obj, cls=EnhancedJSONEncoder, indent=4, sort_keys=False)
