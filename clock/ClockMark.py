from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

MarkType = TypeVar("MarkType")


@dataclass(slots=True)
class ClockMark(Generic[MarkType]):
    """representa una marca del reloj (hora, minuto o segundo)"""

    label: MarkType
    next_mark: ClockMark[MarkType] | None = None
    previous_mark: ClockMark[MarkType] | None = None
