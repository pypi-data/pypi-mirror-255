import typing

from pydantic import Field  # , validator

from ._element import (
    ElementABC,
    ConnectorNotSetError,
    InvalidElementTypeError,
    )


class HeatingContactorRod(ElementABC['HeatingContactor']):

    @property
    def contactor(self) -> 'HeatingContactor':
        contactor = self.parent
        if contactor is None:
            raise ConnectorNotSetError(
                self, 'contactor', [HeatingContactor]
                )
        assert isinstance(contactor, HeatingContactor)
        return contactor

    @contactor.setter
    def contactor(self, contactor: 'HeatingContactor'):
        if not isinstance(contactor, HeatingContactor):
            raise InvalidElementTypeError(
                contactor, [HeatingContactor]
                )
        self.parent = contactor

    def _shv_path(self) -> str:
        return (
            f'devices/heating/{self.contactor.heating}/contactor'
            f'/{self.contactor}/rod/{self.name}'
            )


def is_heating_rod(obj: typing.Any) -> typing.TypeGuard[HeatingContactorRod]:
    return isinstance(obj, HeatingContactorRod)


class _HeatingChild(ElementABC['Heating']):

    @property
    def heating(self) -> 'Heating':
        heating = self.parent
        if heating is None:
            raise ConnectorNotSetError(self, 'heating', [Heating])
        assert isinstance(heating, Heating)
        return heating

    @heating.setter
    def heating(self, heating: 'Heating'):
        if not isinstance(heating, Heating):
            raise InvalidElementTypeError(heating, [Heating])
        self.parent = heating

    def _shv_path(self) -> str:
        raise NotImplementedError


class HeatingContactor(_HeatingChild):
    rods: dict[str, HeatingContactorRod] = Field(default_factory=dict)

    # @validator('rods')
    def _bind_rods(
        self, rods: dict[str, HeatingContactorRod]
    ) -> dict[str, HeatingContactorRod]:
        for rod in rods.values():
            rod.contactor = self
        return rods

    def _shv_path(self) -> str:
        return f'devices/heating/{self.heating}/contactor/{self.name}'


def is_heating_contactor(
    obj: typing.Any
) -> typing.TypeGuard[HeatingContactor]:
    return isinstance(obj, HeatingContactor)


class HeatingMeteo(_HeatingChild):

    def _shv_path(self) -> str:
        return ''


def is_heating_meteo(obj: typing.Any) -> typing.TypeGuard[HeatingMeteo]:
    return isinstance(obj, HeatingMeteo)


class Heating(ElementABC):
    contactors: typing.Mapping[str, HeatingContactor] = Field(
        default_factory=dict
        )
    meteo: typing.Optional[HeatingMeteo] = None

    # @validator('contactors')
    def _bind_contactors(
        self, contactors: dict[str, HeatingContactor]
    ) -> dict[str, HeatingContactor]:
        for cont in contactors.values():
            cont.heating = self
        return contactors

    # @validator('contactors')
    def _bind_meteo(
        self, meteo: typing.Optional[HeatingMeteo]
    ) -> typing.Optional[HeatingMeteo]:
        if not meteo:
            return meteo
        meteo.heating = self
        return meteo

    def _shv_path(self) -> str:
        return f'devices/heating/{self.name}'


def is_heating(obj: typing.Any) -> typing.TypeGuard[Heating]:
    return isinstance(obj, Heating)
