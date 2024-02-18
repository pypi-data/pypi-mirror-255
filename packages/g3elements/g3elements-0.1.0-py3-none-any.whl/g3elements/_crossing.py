import typing

from ._element import ElementABC


class Crossing(ElementABC[None]):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return ''


def is_crossing(obj: typing.Any) -> typing.TypeGuard[Crossing]:
    return isinstance(obj, Crossing)
