from __future__ import annotations

from datetime import datetime, timedelta, timezone

import customtkinter as ctk

from core import WorldClockCarousel, WorldClockNode
from ui.helpers import SchedulerUtils
from utils import ClockAngleUtils, ClockAngles

from .clock_cities import WORLD_CLOCK_CITIES
from .clock_nav import ClockTabNavMixin
from .clock_ui import ClockTabUiMixin


def _local_offset_hours() -> float:
    local_now = datetime.now().astimezone()
    utc_offset = local_now.utcoffset() or timedelta()
    return utc_offset.total_seconds() / 3600.0


def _format_offset(offset_hours: float) -> str:
    sign = "+" if offset_hours >= 0 else "-"
    absolute = abs(offset_hours)
    whole_hours = int(absolute)
    minutes = int(round((absolute - whole_hours) * 60))
    if minutes == 60:
        whole_hours += 1
        minutes = 0
    return f"UTC{sign}{whole_hours:02d}:{minutes:02d}"


class ClockTab(ClockTabNavMixin, ClockTabUiMixin, ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="transparent")

        self._update_job: str | None = None
        self._local_nav_job: str | None = None
        self._local_nav_direction = 0
        self._local_nav_steps_remaining = 0
        self._utc_now_provider = lambda: datetime.now(timezone.utc)
        self._carousel = WorldClockCarousel(self._build_city_dataset())
        self._hover_direction: int | None = None

        self._build_ui()
        self._render_active_city(animate=False)
        self._schedule_tick()

    def destroy(self) -> None:
        SchedulerUtils.cancel_after_job(self, self._update_job)
        self._update_job = None
        SchedulerUtils.cancel_after_job(self, self._local_nav_job)
        self._local_nav_job = None
        super().destroy()

    def _schedule_tick(self) -> None:
        now = datetime.now()
        delay_ms = max(25, 1000 - (now.microsecond // 1000))
        self._update_job = self.after(delay_ms, self._tick)

    def _tick(self) -> None:
        self._render_active_city(animate=False)
        self._schedule_tick()

    def _build_city_dataset(self) -> tuple[tuple[str, float], ...]:
        local_offset = _local_offset_hours()
        cities: list[tuple[str, float]] = []

        for city_name, offset in WORLD_CLOCK_CITIES:
            if city_name == "Local":
                cities.append((city_name, local_offset))
            else:
                cities.append((city_name, offset))

        return tuple(cities)

    def _city_time(self, city: WorldClockNode, utc_now: datetime) -> datetime:
        local_time = utc_now + timedelta(hours=city.timezone_offset)
        return local_time.replace(tzinfo=None)

    @staticmethod
    def _angles_for_time(current_time: datetime) -> ClockAngles:
        return ClockAngleUtils.angles_for_datetime(current_time)

    def _render_active_city(self, *, animate: bool) -> None:
        utc_now = self._utc_now_provider()
        city = self._carousel.current
        city_time = self._city_time(city, utc_now)

        self.city_label.configure(
            text=f"{city.city_name}  |  {_format_offset(city.timezone_offset)}"
        )

        prev_city = self._carousel.node_at_offset(-1)
        next_city = self._carousel.node_at_offset(1)
        self.breadcrumb_label.configure(
            text=(
                f"Anterior: {prev_city.city_name} ({_format_offset(prev_city.timezone_offset)})"
                f"  |  Siguiente: {next_city.city_name} ({_format_offset(next_city.timezone_offset)})"
            )
        )

        if animate:
            self.clock.animate_to_display(city_time)
        else:
            self.clock.set_display(city_time)

        self._sync_preview(utc_now)


def build(parent: ctk.CTkFrame) -> ClockTab:
    return ClockTab(parent)
