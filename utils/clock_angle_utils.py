from __future__ import annotations

from datetime import datetime


class ClockAngleUtils:
    @staticmethod
    def angles_for_datetime(current_time: datetime) -> tuple[float, float, float]:
        hour_value = current_time.hour % 12
        minute_value = current_time.minute
        second_value = current_time.second + (current_time.microsecond / 1_000_000)
        return ClockAngleUtils.angles_for_positions(
            hour_value=hour_value,
            minute_value=minute_value,
            second_value=second_value,
        )

    @staticmethod
    def angles_for_positions(
        *,
        hour_value: float,
        minute_value: float,
        second_value: float,
    ) -> tuple[float, float, float]:
        hour_angle = hour_value * 30 + minute_value * 0.5 + second_value * (0.5 / 60.0)
        minute_angle = minute_value * 6 + second_value * 0.1
        second_angle = second_value * 6
        return hour_angle, minute_angle, second_angle
