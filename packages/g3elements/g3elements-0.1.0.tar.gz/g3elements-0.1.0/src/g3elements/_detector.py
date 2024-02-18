import typing
import enum

from ._element import ElementABC


class DetectorType(enum.StrEnum):
    OTHER = "Detector (unknown type)"
    MASS = "Mass detector"
    PANTOGRAPH = "Pantograph detector"
    TRACKCIRCUIT = "Track circuit detector"
    ULTRASONIC = "Ultrasonic detector"
    VIRTUAL = "Virtual detector"


class Detector(ElementABC):
    type: DetectorType

    def _shv_path(self) -> str:
        return f'devices/detector/{self.name}'


def is_detector(obj: typing.Any) -> typing.TypeGuard[Detector]:
    return isinstance(obj, Detector)
