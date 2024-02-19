from typing import List, Dict, Optional
from dataclasses import dataclass
from copy import deepcopy
from zetsubou.project.model.config_string import VARIANT_STR_DELIMETER, EDefaultConfigSlots

from zetsubou.utils import logger

@dataclass
class ConfigVariant:
    config_string: str
    slots: Dict[str, str]

    def get_slot(self, slot):
        if isinstance(slot, EDefaultConfigSlots):
            return self.slots[slot.name]
        return self.slots[slot]


def get_config_matrix_os_name(config_string: str):
    return config_string.replace('-', '_')


@dataclass
class ConfigMatrix:
    variants: List[ConfigVariant]
    slots: List[str]

    def has_variant(self, variant_string:str):
        return any(filter(lambda v : v.config_string == variant_string, self.variants))

    # Queries variants matching slot values present in dictionary
    # Egx. { 'configuration' : 'DEBUG' }
    def find_variants(self, data: dict):
        results = []

        for variant in self.variants:
            is_variant_ok = True

            for filter_name, filter_value in data.items():
                if filter_name not in self.slots:
                    raise ValueError(f"Unknown slot '{filter_name}'")

                val = variant.get_slot(filter_name)
                if val != filter_value:
                    is_variant_ok = False

            if is_variant_ok:
                results.append(variant)

        return results


def compile_config_variant_name(slots:dict) -> (Optional[str], str):
    try:
        plat = slots[EDefaultConfigSlots.platform.name]
        conf = slots[EDefaultConfigSlots.configuration.name]
        tool = slots[EDefaultConfigSlots.toolchain.name]
        slot_values = [plat, conf, tool]
        return (VARIANT_STR_DELIMETER.join(slot_values))
    except KeyError as e:
        return (None, f"Required slot '{str(e)}' not provided")


def create_config_matrix(domain:dict) -> ConfigMatrix:
    config_variants = []

    for slot_name, values in domain.items():
        if len(values) == 0:
            logger.CriticalError(f'Unable to build list of values for slot \'{slot_name}\'')
            return None

    def RecurseBuildVariants(slot_itr:int=0, field_values={}):
        if slot_itr >= len(domain):
            config_variants.append(ConfigVariant(
                config_string=compile_config_variant_name(field_values),
                slots=deepcopy(field_values)
            ))
        else:
            key, values = list(domain.items())[slot_itr]
            for val in values:
                field_values[key] = val
                RecurseBuildVariants(slot_itr+1, field_values)

    RecurseBuildVariants()

    return ConfigMatrix(variants=config_variants, slots=domain.keys)
