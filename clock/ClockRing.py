from __future__ import annotations

from typing import Generic, Iterable, Iterator

from .ClockMark import ClockMark, MarkType


class ClockRing(Generic[MarkType]):
    """A circular clock path that can be walked in either direction."""

    def __init__(self, marks: Iterable[MarkType]) -> None:
        mark_list = list(marks)
        if not mark_list:
            raise ValueError("ClockRing needs at least one mark.")

        self._marks = self._build_ring(mark_list)
        self._focus = self._marks[0]

    @staticmethod
    def _build_ring(mark_list: list[MarkType]) -> list[ClockMark[MarkType]]:
        marks = [ClockMark(label=label) for label in mark_list]

        for index, mark in enumerate(marks):
            mark.next_mark = marks[(index + 1) % len(marks)]
            mark.previous_mark = marks[(index - 1) % len(marks)]

        return marks

    @property
    def current_mark(self) -> MarkType:
        return self._focus.label

    @property
    def size(self) -> int:
        return len(self._marks)

    def advance(self, steps: int = 1) -> MarkType:
        """Move clockwise around the ring."""

        self._focus = self._walk(self._focus, steps, clockwise=True)
        return self.current_mark

    def rewind(self, steps: int = 1) -> MarkType:
        """Move counterclockwise around the ring."""

        self._focus = self._walk(self._focus, steps, clockwise=False)
        return self.current_mark

    def place_on(self, label: MarkType) -> MarkType:
        """Jump to a specific mark on the ring."""

        for mark in self._marks:
            if mark.label == label:
                self._focus = mark
                return self.current_mark

        raise ValueError(f"Unknown clock mark: {label!r}")

    def sequence(self, starting_label: MarkType | None = None) -> list[MarkType]:
        """Return the ring order, starting from a chosen mark if provided."""

        start = (
            self._focus if starting_label is None else self._mark_for(starting_label)
        )
        ordered: list[MarkType] = []
        current = start

        for _ in range(self.size):
            ordered.append(current.label)
            next_mark = current.next_mark
            if next_mark is None:
                raise RuntimeError("ClockRing links were not built correctly.")
            current = next_mark

        return ordered

    def __iter__(self) -> Iterator[MarkType]:
        return iter(self.sequence())

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"ClockRing(current_mark={self.current_mark!r}, sequence={self.sequence()!r})"

    def _mark_for(self, label: MarkType) -> ClockMark[MarkType]:
        for mark in self._marks:
            if mark.label == label:
                return mark
        raise ValueError(f"Unknown clock mark: {label!r}")

    def _walk(
        self,
        start: ClockMark[MarkType],
        steps: int,
        *,
        clockwise: bool,
    ) -> ClockMark[MarkType]:
        if steps < 0:
            raise ValueError("steps must be non-negative")

        if not self._marks:
            raise RuntimeError("ClockRing is empty.")

        steps = steps % self.size
        current = start

        for _ in range(steps):
            next_mark = current.next_mark if clockwise else current.previous_mark
            if next_mark is None:
                raise RuntimeError("ClockRing links were not built correctly.")
            current = next_mark

        return current
