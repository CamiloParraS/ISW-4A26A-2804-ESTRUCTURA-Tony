from __future__ import annotations

from .ClockRing import ClockRing


class AnalogClockBase:
    """Foundation for later analog-clock behavior."""

    def __init__(self) -> None:
        self.hour_path = ClockRing(range(1, 13))

    @property
    def hour_position(self) -> int:
        return self.hour_path.current_mark

    def tick(self, hours: int = 1) -> int:
        """Advance the clock face by whole hours."""

        return self.hour_path.advance(hours)

    def reverse(self, hours: int = 1) -> int:
        """Move the clock face backwards by whole hours."""

        return self.hour_path.rewind(hours)

    def set_hour(self, hour: int) -> int:
        """Place the hand on a specific hour mark."""

        return self.hour_path.place_on(hour)
