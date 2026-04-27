from __future__ import annotations

from typing import Generic, Iterable

from .ClockEngineNav import ClockEngineNavMixin
from .ClockEngineView import ClockEngineViewMixin
from .ClockMark import ClockMark, MarkType


class ClockEngine(
    ClockEngineNavMixin[MarkType],
    ClockEngineViewMixin[MarkType],
    Generic[MarkType],
):
    """La cosa que representa las horas, minutos o segundos del reloj"""

    def __init__(self, marks: Iterable[MarkType]) -> None:
        mark_list = list(marks)

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
    def current_mark(self) -> MarkType | None:
        if self._current is None:
            return None
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
        else:
            last = self.head.previous_mark or self.head

            new_node.next_mark = self.head
            self.head.previous_mark = new_node
            new_node.previous_mark = last
            last.next_mark = new_node
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
        else:
            last = self.head.previous_mark or self.head

            last.next_mark = new_node
            new_node.next_mark = self.head
            new_node.previous_mark = last
            self.head.previous_mark = new_node
            self._size += 1
            self._node_map[data] = new_node

    def delete(self, data: MarkType) -> None:
        if self.head is None or data not in self._node_map:
            return

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
            return

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
        if current is not None:
            print(current.label)
            current = current.next_mark
        while current != self.head:
            print(current.label)
            current = current.next_mark
