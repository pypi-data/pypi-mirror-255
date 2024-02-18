import typing

from pydantic import Field  # , validator

from .config import SWSystemDictWrapper
from .config.type_hinting import SystemDict, SWDeviceDict

from ._element import ElementABC, Element, ElementType, is_element
from ._cabinet import (
    Cabinet,
    CabinetBRC,
    CabinetControlPanel,
    CabinetConvertor,
    CabinetFuse,
    CabinetMonitoringModule,
    CabinetRFID,
    CabinetUPS,
    # is_cabinet
)
from ._crossing import Crossing, is_crossing
from ._detector import Detector, DetectorType, is_detector
from ._gate import Gate, is_gate
from ._heating import (
    Heating, HeatingContactor, HeatingContactorRod, HeatingMeteo
)
from ._pointmachine import (
    PointMachine,
    PointMachineElectrical,
    PointMachineMechanical,
    is_pm,
)
from ._route import (
    Route,
    RouteLayout,
    RouteLayoutElement,
    RouteLayoutCrossing,
    RouteLayoutDetector,
    RouteLayoutPointMachine,
    PointMachinePosition,
    is_route
)
from ._signal_symbol import Signal, SignalSymbol, CurrMeasType, is_signal
# from ._system import System, SystemSafety
from ._requestor import (
    # Requestor,
    RequestorAWA,
    RequestorDigital,
    RequestorDRR,
    RequestorDRRTransceiver,
    RequestorRoutingTable,
    RequestorSPIE,
    RequestorSPIELoop,
    RequestorVecom,
    RequestorVecomLoop,
    RequestorVetra,
    # RequestorLoopType
)
# from ._gpio import GPIO
from ._matrix import Matrix


def collect_connected(
    element: ElementABC, ignore_zone: bool = True
) -> list[ElementABC]:

    def collect(element: ElementABC, already_collected: list) -> None:
        if (
            any(e is element for e in already_collected) or
            (ignore_zone and isinstance(element, Zone))
        ):
            return
        already_collected.append(element)
        for attr in vars(element).values():
            if isinstance(attr, ElementABC):
                collect(attr, already_collected)
            elif isinstance(attr, typing.Mapping):
                for value in attr.values():
                    if isinstance(value, ElementABC):
                        collect(value, already_collected)
            elif isinstance(attr, typing.Iterable):
                for value in attr:
                    if isinstance(value, str):
                        continue
                    if isinstance(value, ElementABC):
                        collect(value, already_collected)

    collected: list[ElementABC] = []
    collect(element, collected)
    return collected


T = typing.TypeVar('T', bound=typing.Union[ElementABC, dict[str, ElementABC]])


class Zone(ElementABC[None]):
    elements: list[ElementABC] = Field(default_factory=list)

    # @validator('*')
    def _set_zone(self, field: T) -> T:
        if isinstance(field, ElementABC):
            field.zone = self
            for element in collect_connected(field):
                if element.zone != self:
                    element.zone = self
        elif isinstance(field, list):
            for item in field:
                item.zone = self
                for element in collect_connected(item):
                    if element.zone != self:
                        element.zone = self
        return field

    @classmethod
    def from_system_config(cls, zone_name: str, data: SystemDict) -> 'Zone':
        return SystemDictToZoneConverter(zone_name, data).create_zone()

    @property
    def all_elements(self) -> list[ElementABC]:
        return collect_connected(self, ignore_zone=False)

    def find_by_type(
        self, type_: typing.Type[ElementType]
    ) -> list[ElementType]:
        return [
            element for element in self.all_elements
            if is_element(element, of_type=type_)
            ]

    def _shv_path(self) -> str:
        return f'devices/zone/{self.name}'


def is_zone(obj: typing.Any) -> typing.TypeGuard[Zone]:
    return isinstance(obj, Zone)


class SystemDictToZoneConverter:
    TYPES: dict[str, type[ElementABC]] = {
        'zone': Zone,
        'gate': Gate,
        'route': Route,
        'detector': Detector,
        'pme': PointMachineElectrical,
        'pmm': PointMachineMechanical,
        'signal': Signal,
        'symbol': SignalSymbol,
        'matrix': Matrix,
        'routingtable': RequestorRoutingTable,
        'requestordegital': RequestorDigital,
        'vecomcontroller': RequestorVecom,
        'vecomloop': RequestorVecomLoop,
        'vetra': RequestorVetra,
        'spiecontroller': RequestorSPIE,
        'spieloop': RequestorSPIELoop,
        'drrcontroller': RequestorDRR,
        'drrtransceiver': RequestorDRRTransceiver,
        'awa': RequestorAWA,
        'cabinet': Cabinet,
        'brc': CabinetBRC,
        'panel': CabinetControlPanel,
        'convertor': CabinetConvertor,
        'fuse': CabinetFuse,
        'monitoringmodule': CabinetMonitoringModule,
        'rfid': CabinetRFID,
        'ups': CabinetUPS,
        'heating': Heating,
        'meteo': HeatingMeteo,
        'contactor': HeatingContactor,
        'rod': HeatingContactorRod
    }

    def __init__(self, zone_name: str, data: SystemDict) -> None:
        self.zone_name = zone_name
        self.data_wrapper = SWSystemDictWrapper(data['Software'])
        self.elements: dict[str, ElementABC] = {}

    @staticmethod
    def _get_detector_type(type_: str) -> DetectorType:
        types: dict[str, DetectorType] = {
            'trackcircuit': DetectorType.TRACKCIRCUIT,
            'pantographdetector': DetectorType.PANTOGRAPH,
            'massdetector': DetectorType.MASS,
            'ultrasonicsensor': DetectorType.ULTRASONIC,
            'virtualdetector': DetectorType.VIRTUAL
            }
        type_ = type_.replace(' ', '').replace('_', '').casefold()
        return types.get(type_, DetectorType.OTHER)

    @staticmethod
    def _get_curr_meas_type(value: str) -> CurrMeasType:
        if not value:
            return CurrMeasType.NO_MEASUREMENT
        try:
            values = {m.value: m for m in CurrMeasType}
            return values[value.upper()]
        except KeyError:
            raise ValueError(f'Invalid current measurement type: "{value}".')

    def _create_default(
        self, type_: str, data: SWDeviceDict, **kwargs
    ) -> ElementABC:
        element_cls = self.TYPES.get(type_, Element)
        element_name = self.data_wrapper.get_device_name(data)
        element = element_cls(name=element_name, **kwargs)
        element.is_safety = self.data_wrapper.is_device_safety(data)
        element.data['device_dict'] = data
        return element

    def _create_detector(self, data: SWDeviceDict) -> Detector | ElementABC:
        detector_type = data['general'].get('type', '')
        detector_type = self._get_detector_type(detector_type)
        return self._create_default('detector', data, type=detector_type)

    def _create_pm(self, data: SWDeviceDict) -> PointMachine | ElementABC:
        pm_type = data['general'].get('type', '').lower()
        return self._create_default(pm_type, data)

    def _create_symbol(self, data: SWDeviceDict) -> SignalSymbol | ElementABC:
        config = data.get('control', {}).get('config', {})
        curr_meas = self._get_curr_meas_type(config.get('measureCurrent', ''))
        return self._create_default('symbol', data, curr_meas=curr_meas)

    def _create_route_layout(self, data: SWDeviceDict) -> RouteLayout:
        startgate_key = f"Gate/{data['control']['connector']['gate']}"
        startgate = self.elements[startgate_key]
        assert is_gate(startgate)
        length = data['general']['length']
        layout_data: list[dict] = data['general']['layout']
        layout_elements: list[RouteLayoutElement] = []
        element: RouteLayoutElement
        for item_data in layout_data:
            if item_data['type'] == 'detector':
                detector = self.elements[f"Detector/{item_data['name']}"]
                assert is_detector(detector)
                element = RouteLayoutDetector(
                    detector=detector,
                    start_offset=item_data['startoffset'],
                    end_offset=item_data['endoffset'],
                    )
            elif item_data['type'] == 'pointmachine':
                pm = self.elements[f"PointMachine/{item_data['name']}"]
                assert is_pm(pm)
                element = RouteLayoutPointMachine(
                    pointmachine=pm,
                    start_offset=item_data['startoffset'],
                    end_offset=item_data['endoffset'],
                    position=PointMachinePosition(item_data['position'])
                    )
            elif item_data['type'] == 'crossing':
                crossing_name = item_data['name']
                crossing_key = f"Crossing/{crossing_name}"
                crossing = self.elements.setdefault(
                    crossing_key, Crossing(name=crossing_name)
                    )
                crossing.data['device_dict'] = {}
                assert is_crossing(crossing)
                element = RouteLayoutCrossing(
                    crossing=crossing,
                    start_offset=item_data['startoffset'],
                    end_offset=item_data['endoffset'],
                    )
            else:
                raise TypeError(item_data['type'])
            element.data['route_element_dict'] = item_data
            layout_elements.append(element)
        return RouteLayout(startgate, layout_elements, length)

    def _create_route(self, data: SWDeviceDict) -> Route | ElementABC:
        """side effect: creates and adds crossings to elements dict"""
        layout = self._create_route_layout(data)
        return self._create_default('route', data, layout=layout)

    def _create_element(self, type_: str, data: SWDeviceDict) -> ElementABC:
        type_ = type_.casefold()
        # process special cases
        if type_ == 'zone' or type_ == 'route':
            name = self.data_wrapper.get_device_name(data)
            err = f'Cannot create {type_} "{name}" with default initalizer.'
            raise TypeError(err)
        if type_ == 'detector':
            return self._create_detector(data)
        if type_ == 'pointmachine':
            return self._create_pm(data)
        if type_ == 'symbol':
            return self._create_symbol(data)
        # process the rest
        return self._create_default(type_, data)

    def _bind_parent_child(self) -> None:
        iter_devices_zone = self.data_wrapper.iter_devices_zone
        for parent_path, path, _ in iter_devices_zone(self.zone_name):
            if not parent_path or 'Zone' in path:
                continue
            element = self.elements[path]
            parent = self.elements[parent_path]
            element.parent = parent

    def _bind_signal_assigned_element(self) -> None:
        signals: dict[str, Signal] = {}
        gates: dict[str, Gate] = {}
        pms: dict[str, PointMachine] = {}
        for element in self.elements.values():
            if is_signal(element):
                signals[element.name] = element
            elif is_pm(element):
                pms[element.name] = element
            elif is_gate(element):
                gates[element.name] = element
        for signal in signals.values():
            assigned_element_name = (
                signal.data['device_dict']['general']['assigned_element']
            )
            if assigned_element_name in gates:
                signal.assigned_element = gates[assigned_element_name]
            elif assigned_element_name in pms:
                signal.assigned_element = pms[assigned_element_name]

    def _bind_route_go_symbol(self) -> None:
        """should be ran after sh lamps are bound with gates"""
        for element in self.elements.values():
            if not is_route(element):
                continue
            try:
                general_data = element.data['device_dict']['general']
                go_symbol_name = general_data['go_symbol']
                if not go_symbol_name:
                    raise KeyError
            except KeyError:
                continue
            if (
                (sg_lamp := element.layout.gate.sg_lamp) and
                (go_symbol := sg_lamp.symbols.get(go_symbol_name))
            ):
                element.go_symbol = go_symbol

    def _bind_elements(self) -> None:
        self._bind_parent_child()
        self._bind_signal_assigned_element()
        self._bind_route_go_symbol()

    def create_zone(self) -> Zone:
        iter_devices_zone = self.data_wrapper.iter_devices_zone
        # first traversal - init most of the elements, don't bind
        zone_data: SWDeviceDict | None = None
        for _, path, data in iter_devices_zone(self.zone_name):
            element_type = path.split('/')[-2]
            if element_type == 'Zone':
                zone_data = data
                continue
            if element_type == 'Route':
                continue
            self.elements[path] = self._create_element(element_type, data)
        # second traversal - init routes
        for _, path, data in iter_devices_zone(self.zone_name):
            if 'Route' not in path:
                continue
            self.elements[path] = self._create_route(data)
        # bind elements with each other
        self._bind_elements()
        # init zone
        if zone_data is None:
            raise ValueError(
                'Zone device data was not found during '
                'the system configuration data traversal.'
                )
        zone = typing.cast(Zone, self._create_default(
            'zone',
            data=zone_data,
            elements=[e for e in self.elements.values()]
            ))
        for e in zone.elements:
            e.zone = zone
        assert isinstance(zone, Zone)
        return zone
