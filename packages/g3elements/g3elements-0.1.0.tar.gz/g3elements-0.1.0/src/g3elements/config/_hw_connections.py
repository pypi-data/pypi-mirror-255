from g3hardware import HWIsle, HWModuleData
from g3tables import PLCCompositionIOTable

from .type_hinting import HWIsleDict, HWModuleDict


def get_hardware_connections(table: PLCCompositionIOTable) -> list[HWIsleDict]:
    connections: list[HWIsleDict] = []
    isle: HWIsleDict | None = None
    for module_type, cabinet, name_suffix in table.iter_plc_units():
        module_type = HWModuleData.format_module_type(module_type)
        module_dict: HWModuleDict = {
            'type': module_type,
            'cabinet': cabinet,
            'name_suffix': name_suffix
            }
        if HWIsle.is_isle_head(module_type):
            isle = {'head': module_dict, 'tail': []}
            connections.append(isle)
        elif isle is None:
            continue
        else:
            isle['tail'].append(module_dict)
    return connections
