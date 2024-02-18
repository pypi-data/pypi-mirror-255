import typing

from ._element import ElementABC


class System(ElementABC[None]):
    name: str = 'System'
    is_safety: typing.Literal[False] = False

    def _shv_path(self) -> str:
        return 'system'


def is_system(obj: typing.Any) -> typing.TypeGuard[System]:
    return isinstance(obj, System)


class SystemSafety(ElementABC[None]):
    name: str = 'SystemSafety'
    is_safety: typing.Literal[True] = True

    def _shv_path(self) -> str:
        return 'systemSafety'


def is_system_safety(obj: typing.Any) -> typing.TypeGuard[SystemSafety]:
    return isinstance(obj, SystemSafety)
