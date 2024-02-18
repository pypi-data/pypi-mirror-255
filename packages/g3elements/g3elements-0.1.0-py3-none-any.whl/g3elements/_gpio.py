import typing

from ._element import ElementABC


class GPIO(ElementABC):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/gpio/{self.name}'


def is_gpio(obj: typing.Any) -> typing.TypeGuard[GPIO]:
    return isinstance(obj, GPIO)
