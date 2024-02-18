import collections.abc
import typing

# from pydantic import BaseModel

from ._element import ElementABC
from ._crossing import Crossing, is_crossing
from ._gate import Gate
from ._signal_symbol import SignalSymbol
from ._detector import Detector, is_detector
from ._pointmachine import PointMachine, PointMachinePosition, is_pm


class Route(ElementABC[None]):
    layout: 'RouteLayout'
    go_symbol:  typing.Optional[SignalSymbol] = None

    def _shv_path(self) -> str:
        return f'devices/zone/{self.zone}/route/{self.name}'


def is_route(obj: typing.Any) -> typing.TypeGuard[Route]:
    return isinstance(obj, Route)


class RouteLayout(collections.abc.Sequence):
    def __init__(
        self,
        gate: Gate,
        elements: list['RouteLayoutElement'],
        length: float
    ) -> None:
        self._gate = gate
        self._elements = elements
        self._length = length
        self._route: Route | None = None
        self._check_if_layout_valid()
        self._set_element_relations()

    def __str__(self) -> str:
        elements = " -> ".join(e.name for e in self._elements)
        return f'{self._gate} | {elements}'

    def __getitem__(self, index):
        return self._elements[index]

    def __len__(self):
        return len(self._elements)

    def _check_if_layout_valid(self) -> None:
        if not isinstance(self._elements[0], RouteLayoutDetector):
            raise ValueError('Layout must start with a Detector.')
        if not isinstance(self._elements[-1], RouteLayoutDetector):
            raise ValueError('Layout must end with a Detector.')

    def _set_element_relations(self) -> None:
        releaser = (RouteLayoutDetector)
        released = (RouteLayoutCrossing, RouteLayoutPointMachine)
        to_release: list[RouteLayoutCrossing | RouteLayoutPointMachine] = []
        for element in self._elements:
            if isinstance(element, releaser):
                while to_release:
                    dependent_element = to_release.pop(0)
                    dependent_element._add_releaser(element)
                    element._add_dependent_elements(dependent_element)
            elif isinstance(element, released):
                to_release.append(element)

    def get_element(self, element_name: str) -> 'RouteLayoutElement':
        el_name = element_name
        try:
            return next((e for e in self._elements if e.core.name == el_name))
        except StopIteration:
            raise KeyError(f'Layout does not contain element "{el_name}".')

    @property
    def gate(self) -> Gate:
        return self._gate

    @property
    def route(self) -> Route:
        if self._route is None:
            raise AttributeError('Layout is not assosiated with any Route.')
        return self._route

    def _set_route(self, route: 'Route'):
        if not isinstance(route, Route):
            raise ValueError(
                f'Cannot assosiate layout with object "{route}" of type '
                f'"{type(route).__name__}". Expected a "Route" object.'
            )
        self._route = route
        for element in self._elements:
            element._set_route(route)

    @property
    def length(self):
        return self._length


class RouteLayoutElement:
    def __init__(
        self,
        element: ElementABC,
        start_offset: float,
        end_offset: float
    ) -> None:
        super().__init__()
        self._core = element
        self._start_offset = start_offset
        self._end_offset = end_offset
        self._route: typing.Optional[Route] = None
        self._data: dict[typing.Any, typing.Any] = {}

    def __str__(self) -> str:
        route = self._route.name if self._route else "Unknown Route"
        return f'{self._core.name} ({route})'

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(element={self._core}, start_offset='
            f'{self._start_offset}, end_offset={self._end_offset})'
            )

    @property
    def data(self) -> dict[typing.Any, typing.Any]:
        return self._data

    @property
    def core(self) -> ElementABC:
        return self._core

    @property
    def name(self) -> str:
        return self._core.name

    @property
    def layout(self) -> RouteLayout:
        if self._route is None:
            raise AttributeError(
                f'Layout element "{self.name}" is not assosiated with any '
                f'Route Layout.'
                )
        return self._route.layout

    @property
    def route(self) -> Route:
        if self._route is None:
            raise AttributeError(
                f'Layout element "{self.name}" is not assosiated with any '
                f'Route.'
                )
        return self._route

    def _set_route(self, route: Route):
        if not isinstance(route, Route):
            raise ValueError(
                f'Cannot assosiate layout element "{self.name}" with '
                f'object "{route}" of type "{type(route).__name__}". '
                f'Expected a "Route" object.'
            )
        self._route = route


class RouteLayoutDetector(RouteLayoutElement):
    def __init__(
        self,
        detector: Detector,
        start_offset: float,
        end_offset: float,
        releases: typing.Optional[typing.Iterable[
            typing.Union['RouteLayoutPointMachine', 'RouteLayoutCrossing']
            ]] = None,
    ) -> None:
        super().__init__(detector, start_offset, end_offset)
        self._releases = list(releases) if releases else []

    @property
    def core(self) -> Detector:
        core = super().core
        assert is_detector(core)
        return core

    @property
    def releases(
        self
    ) -> list[typing.Union['RouteLayoutPointMachine', 'RouteLayoutCrossing']]:
        return self._releases

    def _add_dependent_elements(
        self,
        *elements: typing.Union[
            'RouteLayoutPointMachine', 'RouteLayoutCrossing'
            ]
    ) -> None:
        expected_element_types = (RouteLayoutPointMachine, RouteLayoutCrossing)
        for element in elements:
            if not isinstance(element, expected_element_types):
                raise ValueError(
                    f'Cannot set detector {self.name} as a releaser of '
                    f'object "{element}" of type "{type(element).__name__}"'
                    f'Expected a "RouteLayoutPointMachine" object or a '
                    f'a "RouteLayoutCrossing" object.'
                )
            if element is self._releases:
                continue
            self._releases.append(element)


class _RouteLayoutReleasedElement(RouteLayoutElement):
    def __init__(
        self,
        element: ElementABC,
        start_offset: float,
        end_offset: float,
        releaser: typing.Optional[RouteLayoutDetector] = None
    ) -> None:
        super().__init__(element, start_offset, end_offset)
        self._releaser = releaser

    @property
    def releaser(self) -> RouteLayoutDetector:
        if self._releaser is None:
            raise AttributeError(
                f'{self.__class__.__name__} "{self.core.name}" '
                f'does not have an assigned releasing Detector.')
        return self._releaser

    def _add_releaser(self, detector: RouteLayoutDetector):
        if not isinstance(detector, RouteLayoutDetector):
            raise ValueError(
                f'Cannot set object "{detector}" of type '
                f'"{type(detector).__name__}" as a releaser of '
                f'{self.__class__.__name__} "{self.name}. '
                f'Expected a "RouteLayoutDetector" object.'
            )
        return self._releaser


class RouteLayoutPointMachine(_RouteLayoutReleasedElement):
    def __init__(
        self,
        pointmachine: PointMachine,
        start_offset: float,
        end_offset: float,
        position: PointMachinePosition,
        releaser: typing.Optional[RouteLayoutDetector] = None
    ) -> None:
        super().__init__(pointmachine, start_offset, end_offset, releaser)
        self._position = position

    @property
    def core(self) -> PointMachine:
        core = super().core
        assert is_pm(core)
        return core

    @property
    def position(self) -> PointMachinePosition:
        return self._position


class RouteLayoutCrossing(_RouteLayoutReleasedElement):
    def __init__(
        self,
        crossing: Crossing,
        start_offset: float,
        end_offset: float,
        releaser: typing.Optional[RouteLayoutDetector] = None
    ) -> None:
        super().__init__(crossing, start_offset, end_offset, releaser)

    @property
    def core(self) -> Crossing:
        core = super().core
        assert is_crossing(core)
        return core
