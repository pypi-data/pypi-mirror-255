import enum
import typing

from pydantic import Field  # , validator

from ._element import ElementABC

if typing.TYPE_CHECKING:
    from ._signal_symbol import Signal


class PointMachinePosition(enum.StrEnum):
    LEFT = "ROUTE_DIRECTION_LEFT"
    RIGHT = "ROUTE_DIRECTION_RIGHT"
    MIDDLE = "ROUTE_DIRECTION_STRAIGHT"


class _PointMachine(ElementABC[None]):
    ppi_signals: dict[str, 'Signal'] = Field(default_factory=dict)

    # @validator('ppi_signals')
    def _bind_ppi_signals(
        self, ppi_signals: dict[str, 'Signal']
    ) -> dict[str, 'Signal']:
        for signal in ppi_signals.values():
            setattr(signal, 'assigned_element', self)
        return ppi_signals

    def _shv_path(self) -> str:
        raise NotImplementedError


class PointMachineElectrical(_PointMachine):

    def _shv_path(self) -> str:
        return f'devices/pointMachine/{self.name}'


class PointMachineMechanical(_PointMachine):

    def _shv_path(self) -> str:
        return f'devices/pointMachine/{self.name}'


PointMachine: typing.TypeAlias = typing.Union[
    PointMachineElectrical, PointMachineMechanical
    ]


def is_pm(
    obj: typing.Any
) -> typing.TypeGuard[PointMachineElectrical | PointMachineMechanical]:
    return isinstance(obj, (PointMachineElectrical, PointMachineMechanical))


def is_pme(obj: typing.Any) -> typing.TypeGuard[PointMachineElectrical]:
    return isinstance(obj, PointMachineElectrical)


def is_pmm(obj: typing.Any) -> typing.TypeGuard[PointMachineMechanical]:
    return isinstance(obj, PointMachineMechanical)
