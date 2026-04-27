from __future__ import annotations

from typing import Generic, Iterator

from .ClockMark import ClockMark, MarkType


class ClockEngineViewMixin(Generic[MarkType]):
    def sequence(self, starting_label: MarkType | None = None) -> list[MarkType]:
        if self.head is None:
            return []

        if starting_label is None:
            start = self._current if self._current is not None else self.head
        else:
            start = self._mark_for(starting_label)

        if start is None:
            return []

        ordered: list[MarkType] = []
        current = start

        for _ in range(self.size):
            ordered.append(current.label)
            next_mark = current.next_mark
            if next_mark is None:
                return ordered
            current = next_mark

        return ordered

    def __iter__(self) -> Iterator[MarkType]:
        return iter(self.sequence())

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"ClockEngine(current_mark={self.current_mark!r}, sequence={self.sequence()!r})"

    def _mark_for(self, label: MarkType) -> ClockMark[MarkType] | None:
        return self._node_map.get(label)
