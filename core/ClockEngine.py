from __future__ import annotations

from typing import Generic, Iterable

from .ClockMark import ClockMark, MarkType
from .ClockEngineNav import ClockEngineNavMixin
from .ClockEngineView import ClockEngineViewMixin


class ClockEngine(
    ClockEngineNavMixin[MarkType],
    ClockEngineViewMixin[MarkType],
    Generic[MarkType],
):
    """La cosa que representa las horas, minutos o segundos del reloj"""

    def __init__(self, marks: Iterable[MarkType]) -> None:
        mark_list = list(marks)
        if not mark_list:
            raise ValueError("ClockEngine needs at least one mark.")

        self.head: ClockMark[MarkType] | None = None
        self._current: ClockMark[MarkType] | None = None
        self._size = 0
        self._node_map: dict[MarkType, ClockMark[MarkType]] = {}

        for index, label in enumerate(mark_list):
            if index == 0:
                self.insert_at_beginning(label)
            else:
                self.insert_at_end(label)

    @property
    def current_mark(self) -> MarkType:
        if self._current is None:
            raise RuntimeError("ClockEngine is empty.")
        return self._current.label

    @property
    def size(self) -> int:
        return self._size

    def insert_at_beginning(self, data: MarkType) -> None:
        new_node = ClockMark(data)

        if self.head is None:
            self.head = new_node
            new_node.next_mark = self.head
            new_node.previous_mark = self.head
            self._current = new_node
            self._size = 1
            self._node_map[data] = new_node
            return

        last = self.head.previous_mark
        if last is None:
            raise RuntimeError("ClockEngine links were not built correctly.")

        new_node.next_mark = self.head
        new_node.previous_mark = last
        last.next_mark = new_node
        self.head.previous_mark = new_node
        self.head = new_node
        self._size += 1
        self._node_map[data] = new_node

    def insert_at_end(self, data: MarkType) -> None:
        new_node = ClockMark(data)

        if self.head is None:
            self.head = new_node
            new_node.next_mark = self.head
            new_node.previous_mark = self.head
            self._current = new_node
            self._size = 1
            self._node_map[data] = new_node
            return

        last = self.head.previous_mark
        if last is None:
            raise RuntimeError("ClockEngine links were not built correctly.")

        last.next_mark = new_node
        new_node.next_mark = self.head
        new_node.previous_mark = last
        self.head.previous_mark = new_node
        self._size += 1
        self._node_map[data] = new_node

    def delete(self, data: MarkType) -> None:
        if self.head is None:
            raise ValueError("ClockEngine is empty.")

        if data not in self._node_map:
            raise ValueError(f"Unknown clock mark: {data!r}")

        current = self._node_map[data]

        if self._size == 1:
            self.head = None
            self._current = None
            self._size = 0
            self._node_map.clear()
            return

        previous_node = current.previous_mark
        next_node = current.next_mark
        if previous_node is None or next_node is None:
            raise RuntimeError("ClockEngine links were not built correctly.")

        previous_node.next_mark = next_node
        next_node.previous_mark = previous_node

        if current is self.head:
            self.head = next_node

        if current is self._current:
            self._current = next_node

        self._size -= 1
        del self._node_map[data]

    def print_list(self) -> None:
        if self.head is None:
            return

        current = self.head
        if current is None:
            raise RuntimeError("ClockEngine links were not built correctly.")

        for _ in range(self._size):
            print(current.label)
            next_node = current.next_mark
            if next_node is None:
                raise RuntimeError("ClockEngine links were not built correctly.")
            current = next_node
