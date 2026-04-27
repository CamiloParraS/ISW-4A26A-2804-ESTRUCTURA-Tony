from __future__ import annotations

import math
import time

from utils import TimeUtils


class CountdownStateMixin:
    def adjust_time(self, delta_seconds: int) -> None:
        if delta_seconds == 0:
            return

        remaining_seconds = max(0, self._remaining_seconds + delta_seconds)
        self._remaining_seconds = remaining_seconds

        hours, minutes, seconds = TimeUtils.from_seconds(remaining_seconds)
        self._normalizing_inputs = True
        try:
            self._hours_var.set(str(hours) if hours >= 100 else f"{hours:02}")
            self._minutes_var.set(f"{minutes:02}")
            self._seconds_var.set(f"{seconds:02}")
        finally:
            self._normalizing_inputs = False

        if self._state == "running" and self._deadline is not None:
            self._deadline = time.monotonic() + remaining_seconds
        elif self._state == "finished" and remaining_seconds > 0:
            self._state = "ready"
            self._deadline = None

        self._refresh_view(animate_clock=True)

    def _tick(self) -> None:
        self._tick_job = None

        if self._state == "running" and self._deadline is not None:
            now = time.monotonic()
            remaining = max(0, int(math.ceil(self._deadline - now)))
            self._remaining_seconds = remaining

            if remaining <= 0:
                self._remaining_seconds = 0
                self._deadline = None
                self._state = "finished"

        self._refresh_view()
        self._schedule_tick()

    def _duration_from_fields(self) -> int:
        hours, minutes, seconds = self._normalize_fields()
        return max(1, TimeUtils.to_seconds(hours, minutes, seconds))

    def start(self) -> None:
        self._remaining_seconds = self._duration_from_fields()
        self._deadline = time.monotonic() + self._remaining_seconds
        self._state = "running"
        self._refresh_view()

    def pause(self) -> None:
        if self._state != "running" or self._deadline is None:
            return

        self._remaining_seconds = max(
            0,
            int(math.ceil(self._deadline - time.monotonic())),
        )
        self._deadline = None
        self._state = "paused"
        self._refresh_view()

    def resume(self) -> None:
        if self._state != "paused" or self._remaining_seconds <= 0:
            return

        self._deadline = time.monotonic() + self._remaining_seconds
        self._state = "running"
        self._refresh_view()

    def reset(self) -> None:
        self._remaining_seconds = self._duration_from_fields()
        self._deadline = None
        self._state = "ready"
        self._refresh_view()
