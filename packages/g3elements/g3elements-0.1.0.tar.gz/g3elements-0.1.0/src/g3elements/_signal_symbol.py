import enum
import typing

from pydantic import Field  # , validator

from ._element import (
    ElementABC,
    ConnectorNotSetError,
    InvalidElementTypeError,
    )
from ._gate import Gate, is_gate
from ._pointmachine import PointMachine, is_pm


AssignedElementType: typing.TypeAlias = typing.Union[Gate, PointMachine]


class Signal(ElementABC[None]):
    symbols: dict[str, 'SignalSymbol'] = Field(default_factory=dict)
    assigned_element: typing.Optional[AssignedElementType] = None

    # @validator('symbols')
    def _set_symbols(
        self, symbols: dict[str, 'SignalSymbol']
    ) -> dict[str, 'SignalSymbol']:
        for symbol in symbols.values():
            symbol.signal = self
        return symbols

    # @validator('assigned_element')
    def _set_assigned_element(
        self, element: AssignedElementType
    ) -> AssignedElementType:
        if not element:
            return element
        if is_gate(element):
            element.sg_lamp = self
        elif is_pm(element):
            element.ppi_signals[self.name] = self
        return element

    def _shv_path(self) -> str:
        return f'devices/signal/{self.name}'


def is_signal(obj: typing.Any) -> typing.TypeGuard[Signal]:
    return isinstance(obj, Signal)


def set_assigned_element(
    signal: Signal, element: typing.Optional[AssignedElementType]
) -> None:
    if not isinstance(signal, Signal):
        raise InvalidElementTypeError(signal, [Signal])
    signal.assigned_element = element


class CurrMeasType(enum.StrEnum):
    """
    Current measurement capabilities:
    - 0 - No measurement;
    - 1 - Warning + Error;
    - 2 - Error;
    - 3 - Warning
    """
    NO_MEASUREMENT = "SIGNAL_SYMBOL_MEASURE_NONE"
    WARNING_ERROR = "SIGNAL_SYMBOL_MEASURE_BOTH"
    ERROR = "SIGNAL_SYMBOL_MEASURE_ERROR"
    WARNING = "SIGNAL_SYMBOL_MEASURE_WARNING"


class SignalSymbol(ElementABC[Signal]):
    curr_meas: CurrMeasType = CurrMeasType.NO_MEASUREMENT

    @property
    def signal(self) -> Signal:
        signal = self.parent
        if signal is None:
            raise ConnectorNotSetError(self, 'signal', [Signal])
        assert isinstance(signal, Signal)
        return signal

    @signal.setter
    def signal(self, signal: Signal):
        if not is_signal(signal):
            raise InvalidElementTypeError(signal, [Signal])
        self.parent = signal

    @property
    def measures_warning(self) -> bool:
        return self.curr_meas in [
            CurrMeasType.WARNING,
            CurrMeasType.WARNING_ERROR
            ]

    @property
    def measures_error(self) -> bool:
        return self.curr_meas in [
            CurrMeasType.ERROR,
            CurrMeasType.WARNING_ERROR
            ]

    def _shv_path(self) -> str:
        return f'devices/signal/{self.signal}/symbol/{self.name}'


def is_symbol(obj: typing.Any) -> typing.TypeGuard[SignalSymbol]:
    return isinstance(obj, SignalSymbol)
