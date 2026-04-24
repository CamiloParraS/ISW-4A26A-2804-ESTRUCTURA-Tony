from __future__ import annotations

from .ClockEngine import ClockEngine


class AnalogClockBase:
    """Lo que luego se va a convertir en un reloj analogico completo."""

    def __init__(self) -> None:
        self.hour_path = ClockEngine(range(1, 13))

    @property
    def hour_position(self) -> int:
        return self.hour_path.current_mark

    def tick(self, hours: int = 1) -> int:
        """Adelanta el reloj por horas"""

        return self.hour_path.advance(hours)

    def reverse(self, hours: int = 1) -> int:
        """Regresa el reloj por horas"""

        return self.hour_path.rewind(hours)

    def set_hour(self, hour: int) -> int:
        """Poner la manesillad en una hora en especfica"""

        return self.hour_path.place_on(hour)
