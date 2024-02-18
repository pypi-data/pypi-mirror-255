import abc
import typing

from pydantic import BaseModel, Field, validator, ConfigDict

if typing.TYPE_CHECKING:
    from ._zone import Zone


ElementType = typing.TypeVar(
    'ElementType', bound='ElementABC'
    )

OptionalElementType = typing.TypeVar(
    'OptionalElementType', bound=typing.Optional['ElementABC']
    )


class ElementABC(BaseModel, abc.ABC, typing.Generic[OptionalElementType]):
    name: str
    is_safety: bool = False
    parent: typing.Optional[OptionalElementType] = None
    zone: typing.Optional['Zone'] = None
    data: dict = Field(default_factory=dict, exclude=True, frozen=True)
    model_config = ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True
        )

    def __str__(self) -> str:
        return self.name

    @validator('name')
    @classmethod
    def _check_name(cls, name: str) -> str:
        if not isinstance(name, str):
            raise ValueError(f'Name "{name}" is not a string.')
        if not name:
            raise ValueError('Name cannot be empty.')
        if not name.replace('_', '').isalnum():
            raise ValueError(
                f'Name "{name}" contains a non-alphanumeric character.'
                )
        return name

    @abc.abstractmethod
    def _shv_path(self) -> str:
        ...

    @property
    def shv_path(self) -> str:
        return self._shv_path()


class Element(ElementABC):

    def _shv_path(self) -> str:
        return ''


@typing.overload
def is_element(
    obj: typing.Any, of_type: typing.Type[ElementType]
) -> typing.TypeGuard[ElementType]: ...


@typing.overload
def is_element(
    obj: typing.Any, of_type: None = None
) -> typing.TypeGuard[ElementABC]: ...


def is_element(
    obj: typing.Any, of_type: typing.Optional[typing.Type[ElementType]] = None
) -> typing.TypeGuard[typing.Union[ElementABC, ElementType]]:
    if of_type is None:
        return isinstance(obj, ElementABC)
    return isinstance(obj, ElementABC) and isinstance(obj, of_type)


ConnectorCallable: typing.TypeAlias = typing.Callable[
    [ElementType, OptionalElementType], None
    ]


def get_connected_element_dict(
    elements: typing.Iterable[ElementType] | None,
    connect_to: typing.Optional[ElementABC] = None,
    connector: ConnectorCallable | None = None
) -> dict[str, ElementType]:
    if not elements:
        elements = []
    elements_dict: dict[str, ElementType] = {}
    for element in elements:
        if is_element(element) and (key := getattr(element, 'name', '')):
            elements_dict[key] = element  # type: ignore
            if connector:
                connector(element, connect_to)
    return elements_dict


def set_parent(element: ElementABC, parent: ElementABC | None) -> None:
    element.parent = parent


def is_iterable(obj):
    if isinstance(obj, str):
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class ConnectorNotSetError(AttributeError):
    def __init__(
        self,
        element: ElementABC,
        connector_name: str,
        allowed_connector_types: typing.Optional[
            typing.Iterable[typing.Type[ElementABC]]
            ] = None
    ) -> None:
        if allowed_connector_types:
            required_element_types = ", ".join(
                f'"{t.__class__.__name__}"' for t in allowed_connector_types
            )
        else:
            required_element_types = '"ElementABC"'
        message = (
            f'{element.__class__.__name__} {element.name}\'s '
            f'"{connector_name}" connector is not associated with any '
            f'elements of type {required_element_types}.'
        )
        super().__init__(message)


class InvalidElementTypeError(TypeError):
    def __init__(
        self,
        element: ElementABC | typing.Any,
        expected_element_types: typing.Optional[
            typing.Iterable[typing.Type[ElementABC]]
            ] = None
    ) -> None:
        if expected_element_types:
            expected_types = ", ".join(
                f'"{t.__class__.__name__}"' for t in expected_element_types
            )
            expected_phrase = (
                f'one of the following element types: {expected_types}, '
            )
        else:
            expected_phrase = 'an object of type "ElementABC", '
        obj_type = 'element' if isinstance(element, ElementABC) else 'object'
        actual_type = element.__class__.__name__
        actual_phrase = f'got a {obj_type} of type "{actual_type}".'
        message = f'Expected {expected_phrase}{actual_phrase}'
        super().__init__(message)
