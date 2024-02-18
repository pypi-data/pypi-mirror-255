import typing

# from pydantic import validator

from ._element import ElementABC

if typing.TYPE_CHECKING:
    from ._signal_symbol import Signal


class Gate(ElementABC):
    sg_lamp: typing.Optional['Signal'] = None

    # @validator('sg_lamp')
    def _bind_sg_lamp(self, sg_lamp: 'Signal') -> 'Signal':
        sg_lamp.assigned_element = self
        return sg_lamp

    def _shv_path(self) -> str:
        return f'devices/zone/{self.zone}/gate/{self.name}'


def is_gate(obj: typing.Any) -> typing.TypeGuard[Gate]:
    return isinstance(obj, Gate)
