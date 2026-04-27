from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class WorldClockNode:
    city_name: str
    timezone_offset: float
    next: "WorldClockNode | None" = None
    prev: "WorldClockNode | None" = None


class WorldClockCarousel:
    """Circular doubly linked list used to rotate world clock cities."""

    def __init__(self, cities: Iterable[tuple[str, float]]) -> None:
        city_list = list(cities)
        if not city_list:
            self._size = 0
            self._current = None
            return

        nodes = [WorldClockNode(name, offset) for name, offset in city_list]
        size = len(nodes)

        for index, node in enumerate(nodes):
            node.next = nodes[(index + 1) % size]
            node.prev = nodes[(index - 1) % size]

        self._size = size
        self._current = nodes[0]

    @property
    def current(self) -> WorldClockNode | None:
        return self._current

    @property
    def size(self) -> int:
        return self._size

    def has_city(self, city_name: str) -> bool:
        if self._current is None:
            return False
        return self._steps_to_city(city_name, clockwise=True) is not None

    def shortest_offset_to_city(self, city_name: str) -> int:
        """Return the signed shortest offset from current city to target city.

        Positive values mean clockwise (next) traversal.
        Negative values mean counterclockwise (previous) traversal.
        """
        if self._current is None:
            return 0

        clockwise_steps = self._steps_to_city(city_name, clockwise=True)
        counterclockwise_steps = self._steps_to_city(city_name, clockwise=False)

        if clockwise_steps is None or counterclockwise_steps is None:
            return 0

        if clockwise_steps <= counterclockwise_steps:
            return clockwise_steps
        return -counterclockwise_steps

    def _steps_to_city(self, city_name: str, *, clockwise: bool) -> int | None:
        if self._current is None:
            return None

        node = self._current
        for step in range(self._size):
            if node.city_name == city_name:
                return step
            next_node = node.next if clockwise else node.prev
            if next_node is None:
                return None
            node = next_node
        return None

    def rotate_next(self, steps: int = 1) -> WorldClockNode | None:
        return self._move(steps=steps, clockwise=True)

    def rotate_prev(self, steps: int = 1) -> WorldClockNode | None:
        return self._move(steps=steps, clockwise=False)

    def node_at_offset(self, offset: int) -> WorldClockNode | None:
        if self._current is None:
            return None

        if offset == 0:
            return self._current

        clockwise = offset > 0
        if self._size == 0:
            return self._current

        steps = abs(offset) % self._size
        node = self._current

        for _ in range(steps):
            next_node = node.next if clockwise else node.prev
            if next_node is None:
                return node
            node = next_node

        return node

    def _move(self, *, steps: int, clockwise: bool) -> WorldClockNode | None:
        if self._current is None:
            return None

        if steps < 0:
            return self._current

        if steps == 0:
            return self._current

        if self._size == 0:
            return self._current

        steps = steps % self._size
        for _ in range(steps):
            next_node = self._current.next if clockwise else self._current.prev
            if next_node is None:
                return self._current
            self._current = next_node

        return self._current
