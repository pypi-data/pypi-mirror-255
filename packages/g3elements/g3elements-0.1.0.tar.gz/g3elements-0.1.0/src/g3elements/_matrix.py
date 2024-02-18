import typing

from ._element import ElementABC


class Matrix(ElementABC):
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return f'devices/signal/{self.name}'


def is_matrix(obj: typing.Any) -> typing.TypeGuard[Matrix]:
    return isinstance(obj, Matrix)
