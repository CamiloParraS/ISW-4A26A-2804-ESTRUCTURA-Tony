from __future__ import annotations

from typing import Generic, Iterable, Iterator

from .ClockMark import ClockMark, MarkType


class ClockEngine(Generic[MarkType]):
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
        assert current is not None

        for _ in range(self._size):
            print(current.label)
            next_node = current.next_mark
            if next_node is None:
                raise RuntimeError("ClockEngine links were not built correctly.")
            current = next_node

    def advance(self, steps: int = 1) -> MarkType:
        """Move clockwise around the ring."""

        if self._current is None:
            raise RuntimeError("ClockEngine is empty.")

        self._current = self._walk(self._current, steps, clockwise=True)
        return self.current_mark

    def rewind(self, steps: int = 1) -> MarkType:
        """Move counterclockwise around the ring."""

        if self._current is None:
            raise RuntimeError("ClockEngine is empty.")

        self._current = self._walk(self._current, steps, clockwise=False)
        return self.current_mark

    def place_on(self, label: MarkType) -> MarkType:
        """Jump to a specific mark on the ring."""

        if self.head is None:
            raise RuntimeError("ClockEngine is empty.")

        if label not in self._node_map:
            raise ValueError(f"Unknown clock mark: {label!r}")

        self._current = self._node_map[label]
        return self.current_mark

    def sequence(self, starting_label: MarkType | None = None) -> list[MarkType]:
        """Retorna el reloj de alguna forma."""

        if self.head is None:
            return []

        if starting_label is None:
            if self._current is None:
                # If _current isn't set, start from head (we already ensured head is not None above)
                assert self.head is not None
                start = self.head
            else:
                start = self._current
        else:
            start = self._mark_for(starting_label)

        ordered: list[MarkType] = []
        current = start
        assert current is not None

        for _ in range(self.size):
            ordered.append(current.label)
            next_mark = current.next_mark
            if next_mark is None:
                raise RuntimeError("ClockEngine links were not built correctly.")
            current = next_mark

        return ordered

    def __iter__(self) -> Iterator[MarkType]:
        return iter(self.sequence())

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"ClockEngine(current_mark={self.current_mark!r}, sequence={self.sequence()!r})"

    def _mark_for(self, label: MarkType) -> ClockMark[MarkType]:
        if label not in self._node_map:
            raise ValueError(f"Unknown clock mark: {label!r}")
        return self._node_map[label]

    def _walk(
        self,
        start: ClockMark[MarkType],
        steps: int,
        *,
        clockwise: bool,
    ) -> ClockMark[MarkType]:
        if steps < 0:
            raise ValueError("steps must be non-negative")

        if self.head is None:
            raise RuntimeError("ClockEngine is empty.")

        steps = steps % self.size
        current = start

        for _ in range(steps):
            next_mark = current.next_mark if clockwise else current.previous_mark
            if next_mark is None:
                raise RuntimeError("ClockEngine links were not built correctly.")
            current = next_mark

        return current
