import yaml
from yaml.emitter import Emitter

def to_yaml(obj):
    Emitter.prepare_tag = lambda self, tag: ''
    return yaml.dump(data=obj, Dumper=yaml.Dumper, indent=2, sort_keys=False)
