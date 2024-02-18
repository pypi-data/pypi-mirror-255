import enum
import typing

from pydantic import Field  # , validator

from ._element import (
    ElementABC,
    ConnectorNotSetError,
    InvalidElementTypeError,
)


# GENERAL


class RequestorLoopFunction(enum.StrEnum):
    LOGIN = "Login"
    LOGOUT = "Logout"
    LOGIN_LOGOUT = "Login and Logout"
    OTHER = "Other"


class _Requestor(ElementABC[None]):

    def _shv_path(self) -> str:
        raise NotImplementedError


def is_requestor(obj: typing.Any) -> typing.TypeGuard[_Requestor]:
    return isinstance(obj, _Requestor)


RequestorType = typing.TypeVar('RequestorType', bound=_Requestor)


class _RequestorLoop(ElementABC[RequestorType]):
    is_safety: typing.Literal[False] = False
    loop_func: RequestorLoopFunction = RequestorLoopFunction.OTHER

    @property
    def requestor(self) -> _Requestor:
        requestor = self.parent
        if requestor is None:
            raise ConnectorNotSetError(self, 'requestor', [_Requestor])
        assert isinstance(requestor, _Requestor)
        return requestor

    @requestor.setter
    def requestor(self, requestor: _Requestor) -> None:
        if not isinstance(requestor, _Requestor):
            raise InvalidElementTypeError(requestor, _Requestor)
        setattr(self, 'parent', requestor)

    def _shv_path(self) -> str:
        raise NotImplementedError


def is_requestor_loop(obj: typing.Any) -> typing.TypeGuard[_RequestorLoop]:
    return isinstance(obj, _RequestorLoop)


RequestorLoopType = typing.TypeVar('RequestorLoopType', bound=_RequestorLoop)


def set_requestor(
    loops: dict[str, RequestorLoopType], requestor: RequestorType
) -> dict[str, RequestorLoopType]:
    for loop in loops.values():
        loop.requestor = requestor
    return loops


# DIGITAL REQUESTOR


class RequestorDigital(_Requestor):

    def _shv_path(self) -> str:
        return f'devices/localRouteSelector/{self.name}'


def is_digreq(obj: typing.Any) -> typing.TypeGuard[RequestorDigital]:
    return isinstance(obj, RequestorDigital)


# ROUTING TABLE


class RequestorRoutingTable(_Requestor):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return 'devices/routing/table'


def is_routing_table(
    obj: typing.Any
) -> typing.TypeGuard[RequestorRoutingTable]:
    return isinstance(obj, RequestorRoutingTable)


# VETRA


class RequestorVetra(_Requestor):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.name}'


def is_vetra(obj: typing.Any) -> typing.TypeGuard[RequestorVetra]:
    return isinstance(obj, RequestorVetra)


# VECOM

class RequestorVecom(_Requestor):
    is_safety: typing.Literal[False] = False
    loops: dict[str, 'RequestorVecomLoop'] = Field(default_factory=dict)

    # @validator('loops')
    def _set_loops(
        self, loops: dict[str, 'RequestorVecomLoop']
    ) -> dict[str, 'RequestorVecomLoop']:
        return set_requestor(loops, self)

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.name}'


def is_vecom(obj: typing.Any) -> typing.TypeGuard[RequestorVecom]:
    return isinstance(obj, RequestorVecom)


class RequestorVecomLoop(_RequestorLoop[RequestorVecom]):

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.requestor}/loop/{self.name}'


def is_vecom_loop(obj: typing.Any) -> typing.TypeGuard[RequestorVecomLoop]:
    return isinstance(obj, RequestorVecomLoop)


# SPIE


class RequestorSPIE(_Requestor):
    is_safety: typing.Literal[False] = False
    loops: dict[str, 'RequestorSPIELoop'] = Field(default_factory=dict)

    # @validator('loops')
    def _set_loops(
        self, loops: dict[str, 'RequestorSPIELoop']
    ) -> dict[str, 'RequestorSPIELoop']:
        return set_requestor(loops, self)

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.name}'


def is_spie(obj: typing.Any) -> typing.TypeGuard[RequestorSPIE]:
    return isinstance(obj, RequestorSPIE)


class RequestorSPIELoop(_RequestorLoop[RequestorSPIE]):

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.requestor}/loop/{self.name}'


def is_spie_loop(obj: typing.Any) -> typing.TypeGuard[RequestorSPIELoop]:
    return isinstance(obj, RequestorSPIELoop)


# DRR


class RequestorDRR(_Requestor):
    is_safety: typing.Literal[False] = False
    transceivers: dict[str, 'RequestorSPIELoop'] = Field(default_factory=dict)

    # @validator('loops')
    def _set_transceivers(
        self, transceivers: dict[str, 'RequestorSPIELoop']
    ) -> dict[str, 'RequestorSPIELoop']:
        return set_requestor(transceivers, self)

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.name}'


def is_drr(obj: typing.Any) -> typing.TypeGuard[RequestorDRR]:
    return isinstance(obj, RequestorDRR)


class RequestorDRRTransceiver(_RequestorLoop[RequestorDRR]):

    def _shv_path(self) -> str:
        return (
            f'devices/vehicleCommunicator/{self.requestor}'
            f'/transceiver/{self.name}'
            )


def is_drr_transceiver(
    obj: typing.Any
) -> typing.TypeGuard[RequestorDRRTransceiver]:
    return isinstance(obj, RequestorDRRTransceiver)


# AWA


class RequestorAWA(_Requestor):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/vehicleCommunicator/{self.name}'


def is_awa(obj: typing.Any) -> typing.TypeGuard[RequestorAWA]:
    return isinstance(obj, RequestorAWA)


Requestor: typing.TypeAlias = typing.Union[
    _Requestor,
    RequestorDigital,
    RequestorRoutingTable,
    RequestorVetra,
    RequestorVecom,
    RequestorDRR,
    RequestorSPIE,
    RequestorAWA
    ]
