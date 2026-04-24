from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

MarkType = TypeVar("MarkType")


@dataclass(slots=True)
class ClockMark(Generic[MarkType]):
    """A single node in the circular doubly linked list."""

    data: MarkType
    prev: ClockMark[MarkType] | None = None
    next: ClockMark[MarkType] | None = None

    @property
    def label(self) -> MarkType:
        return self.data

    @label.setter
    def label(self, value: MarkType) -> None:
        self.data = value

    @property
    def next_mark(self) -> ClockMark[MarkType] | None:
        return self.next

    @next_mark.setter
    def next_mark(self, value: ClockMark[MarkType] | None) -> None:
        self.next = value

    @property
    def previous_mark(self) -> ClockMark[MarkType] | None:
        return self.prev

    @previous_mark.setter
    def previous_mark(self, value: ClockMark[MarkType] | None) -> None:
        self.prev = value
