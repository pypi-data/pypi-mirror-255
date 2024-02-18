from ._cabinet import (
    Cabinet,
    CabinetBRC,
    CabinetControlPanel,
    CabinetConvertor,
    CabinetFuse,
    CabinetMonitoringModule,
    CabinetRFID,
    CabinetUPS,
    is_brc,
    is_cabinet,
    is_control_panel,
    is_fuse,
)
from ._crossing import Crossing, is_crossing
from ._detector import (
    Detector,
    is_detector
)
from ._element import (
    ElementABC,
    Element,
    ElementType,
    is_element,
)
from ._gate import Gate, is_gate
from ._gpio import GPIO, is_gpio
from ._heating import (
    Heating,
    HeatingContactor,
    HeatingContactorRod,
    HeatingMeteo,
    is_heating,
    is_heating_contactor,
    is_heating_meteo,
    is_heating_rod
)
from ._matrix import Matrix, is_matrix
from ._pointmachine import (
    PointMachine,
    PointMachineElectrical,
    PointMachineMechanical,
    is_pm,
    is_pme,
    is_pmm
)
from ._requestor import (
    Requestor,
    RequestorDigital,
    RequestorDRR,
    RequestorDRRTransceiver,
    RequestorRoutingTable,
    RequestorSPIE,
    RequestorSPIELoop,
    RequestorVecom,
    RequestorVecomLoop,
    RequestorVetra,
    RequestorLoopType,
    is_digreq,
    is_drr,
    is_drr_transceiver,
    is_requestor,
    is_routing_table,
    is_spie,
    is_spie_loop,
    is_vecom,
    is_vecom_loop,
    is_vetra
)
from ._route import (
    Route,
    RouteLayout,
    RouteLayoutCrossing,
    RouteLayoutDetector,
    RouteLayoutPointMachine,
    is_route
)
from ._signal_symbol import (
    Signal,
    SignalSymbol,
    CurrMeasType,
    is_signal,
    is_symbol
)
from ._system import (
    System,
    SystemSafety,
    is_system,
    is_system_safety
)
from ._zone import Zone, is_zone
from . import config


__all__ = [
    'Cabinet',
    'CabinetBRC',
    'CabinetControlPanel',
    'CabinetConvertor',
    'CabinetFuse',
    'CabinetMonitoringModule',
    'CabinetRFID',
    'CabinetUPS',
    'Crossing',
    'Detector',
    'ElementABC',
    'Element',
    'ElementType',
    'Gate',
    'GPIO',
    'Heating',
    'HeatingContactor',
    'HeatingContactorRod',
    'HeatingMeteo',
    'Matrix',
    'PointMachine',
    'PointMachineElectrical',
    'PointMachineMechanical',
    'Requestor',
    'RequestorDigital',
    'RequestorDRR',
    'RequestorDRRTransceiver',
    'RequestorRoutingTable',
    'RequestorSPIE',
    'RequestorSPIELoop',
    'RequestorVecom',
    'RequestorVecomLoop',
    'RequestorVetra',
    'RequestorLoopType',
    'Route',
    'RouteLayout',
    'RouteLayoutCrossing',
    'RouteLayoutDetector',
    'RouteLayoutPointMachine',
    'Signal',
    'SignalSymbol',
    'CurrMeasType',
    'System',
    'SystemSafety',
    'Zone',
    'is_brc',
    'is_cabinet',
    'is_control_panel',
    'is_crossing',
    'is_detector',
    'is_digreq',
    'is_drr',
    'is_drr_transceiver',
    'is_element',
    'is_fuse',
    'is_gate',
    'is_gpio',
    'is_heating',
    'is_heating_contactor',
    'is_heating_meteo',
    'is_heating_rod',
    'is_matrix',
    'is_pm',
    'is_pme',
    'is_pmm',
    'is_requestor',
    'is_routing_table',
    'is_route',
    'is_signal',
    'is_spie',
    'is_spie_loop',
    'is_symbol',
    'is_system',
    'is_system_safety',
    'is_vecom',
    'is_vecom_loop',
    'is_vetra',
    'is_zone',
    'config'
]


for model in [m for m in globals().values()]:
    try:
        model.model_rebuild()
    except AttributeError:
        pass
