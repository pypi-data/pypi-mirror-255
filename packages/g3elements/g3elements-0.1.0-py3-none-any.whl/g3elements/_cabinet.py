import typing

from pydantic import Field  # , validator

from ._element import (
    ElementABC,
    ElementType,
    ConnectorNotSetError,
    InvalidElementTypeError,
    )


class _CabinetChild(ElementABC['Cabinet']):

    @property
    def cabinet(self) -> 'Cabinet':
        cabinet = self.parent
        if cabinet is None:
            raise ConnectorNotSetError(self, 'cabinet', [Cabinet])
        assert isinstance(cabinet, Cabinet)
        return cabinet

    @cabinet.setter
    def cabinet(self, cabinet: 'Cabinet'):
        if not isinstance(cabinet, Cabinet):
            raise InvalidElementTypeError(cabinet, [Cabinet])
        self.parent = cabinet

    def _shv_path(self) -> str:
        raise NotImplementedError


class CabinetControlPanel(_CabinetChild):

    def _shv_path(self) -> str:
        return ''


def is_control_panel(obj: typing.Any) -> typing.TypeGuard[CabinetControlPanel]:
    return isinstance(obj, CabinetControlPanel)


class CabinetConvertor(_CabinetChild):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/cabinet/{self.cabinet}/convertor/{self.name}'


def is_convertor(obj: typing.Any) -> typing.TypeGuard[CabinetControlPanel]:
    return isinstance(obj, CabinetControlPanel)


class CabinetFuse(_CabinetChild):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/cabinet/{self.cabinet}/fuse/{self.name}'


def is_fuse(obj: typing.Any) -> typing.TypeGuard[CabinetFuse]:
    return isinstance(obj, CabinetFuse)


class CabinetBRC(_CabinetChild):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return ''


def is_brc(obj: typing.Any) -> typing.TypeGuard[CabinetBRC]:
    return isinstance(obj, CabinetBRC)


class CabinetMonitoringModule(_CabinetChild):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return ''


def is_monitoring_module(
    obj: typing.Any
) -> typing.TypeGuard[CabinetMonitoringModule]:
    return isinstance(obj, CabinetMonitoringModule)


class CabinetRFID(_CabinetChild):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return ''


def is_rfid(obj: typing.Any) -> typing.TypeGuard[CabinetRFID]:
    return isinstance(obj, CabinetRFID)


class CabinetUPS(_CabinetChild):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/cabinet/{self.cabinet}/ups/{self.name}'


def is_ups(obj: typing.Any) -> typing.TypeGuard[CabinetUPS]:
    return isinstance(obj, CabinetUPS)


class Cabinet(ElementABC):
    brc: typing.Optional[CabinetBRC] = None
    panel: typing.Optional[CabinetControlPanel] = None
    module: typing.Optional[CabinetMonitoringModule] = None
    rfid: typing.Optional[CabinetRFID] = None
    ups: typing.Optional[CabinetUPS] = None
    convertors: dict[str, CabinetConvertor] = Field(default_factory=dict)
    fuses: dict[str, CabinetFuse] = Field(default_factory=dict)

    def _bind_element(self, element: ElementType) -> ElementType:
        if element is None:
            return None
        setattr(element, 'cabinet', self)
        return element

    # @validator('brc', 'panel', 'module', 'rfid', 'ups')
    def _bind_single(self, element: ElementType) -> ElementType:
        return self._bind_element(element)

    # @validator('convertors', 'fuses')
    def _bind_mapping(
        self, elements: dict[str, ElementType]
    ) -> dict[str, ElementType]:
        for element in elements.values():
            self._bind_element(element)
        return elements

    def _shv_path(self) -> str:
        return f'devices/cabinet/{self.name}'


def is_cabinet(obj: typing.Any) -> typing.TypeGuard[Cabinet]:
    return isinstance(obj, Cabinet)
