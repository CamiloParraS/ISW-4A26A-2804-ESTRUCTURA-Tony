from __future__ import annotations

from typing import Generic

from .ClockMark import ClockMark, MarkType


class ClockEngineNavMixin(Generic[MarkType]):
    """Navigation behavior over the circular doubly linked list."""

    def advance(self, steps: int = 1) -> MarkType | None:
        """Move clockwise around the ring."""
        if self._current is None:
            self._current = self.head
        if self._current is None:
            return self.current_mark

        self._current = self._walk(self._current, steps, clockwise=True)
        return self.current_mark

    def rewind(self, steps: int = 1) -> MarkType | None:
        """Move counterclockwise around the ring."""
        if self._current is None:
            self._current = self.head
        if self._current is None:
            return self.current_mark

        self._current = self._walk(self._current, steps, clockwise=False)
        return self.current_mark

    def place_on(self, label: MarkType) -> MarkType | None:
        """Jump to a specific mark by walking the ring from current position."""
        if self.head is None:
            return self.current_mark

        if label not in self._node_map:
            return self.current_mark

        if self._current is None:
            self._current = self.head

        cw_steps = self._steps_to(label, clockwise=True)
        ccw_steps = self._steps_to(label, clockwise=False)

        if self._current is None:
            return self.current_mark

        if cw_steps <= ccw_steps:
            self._current = self._walk(self._current, cw_steps, clockwise=True)
        else:
            self._current = self._walk(self._current, ccw_steps, clockwise=False)

        return self.current_mark

    def _steps_to(self, label: MarkType, *, clockwise: bool) -> int:
        if self._current is None:
            return 0

        node = self._current
        for step in range(self._size):
            if node.label == label:
                return step
            next_node = node.next_mark if clockwise else node.previous_mark
            if next_node is None:
                return self._size
            node = next_node

        return self._size

    def _walk(
        self,
        start: ClockMark[MarkType],
        steps: int,
        *,
        clockwise: bool,
    ) -> ClockMark[MarkType]:
        if steps < 0:
            return start

        if self.head is None:
            return start

        if self._size <= 0:
            return start

        current = start
        for _ in range(steps % self._size):
            next_mark = current.next_mark if clockwise else current.previous_mark
            if next_mark is None:
                return current
            current = next_mark

        return current
