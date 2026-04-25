from __future__ import annotations

from .ClockEngine import ClockEngine


class AnalogClockBase:
    """Lo que luego se va a convertir en un reloj analogico completo."""

    def __init__(self) -> None:
        self.hour_path = ClockEngine(range(1, 13))
        self.minute_path = ClockEngine(range(60))
        self.second_path = ClockEngine(range(60))

    @property
    def hour_position(self) -> int:
        return self.hour_path.current_mark

    @property
    def minute_position(self) -> int:
        return self.minute_path.current_mark

    @property
    def second_position(self) -> int:
        return self.second_path.current_mark

    def sync_time(self, hour: int, minute: int, second: int) -> None:
        """Poner la manesillad en una hora en especifica"""
        hour_val = hour % 12 or 12
        self.hour_path.place_on(hour_val)
        self.minute_path.place_on(minute)
        self.second_path.place_on(second)

    def tick(self) -> None:
        """Avanza el reloj 1 segundo y al resto"""
        sec = self.second_path.advance(1)
        if sec == 0:
            mi = self.minute_path.advance(1)
            if mi == 0:
                self.hour_path.advance(1)

    def reverse(self) -> None:
        """Regresa el reloj 1 segundo y el resto"""
        sec = self.second_path.rewind(1)
        if sec == 59:
            mi = self.minute_path.rewind(1)
            if mi == 59:
                self.hour_path.rewind(1)
