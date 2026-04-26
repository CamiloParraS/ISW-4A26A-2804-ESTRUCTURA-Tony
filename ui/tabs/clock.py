from __future__ import annotations

from datetime import datetime, timedelta, timezone

import customtkinter as ctk

from core import WorldClockCarousel, WorldClockNode
from ui.helpers import SchedulerUtils
from ui.widgets import AnalogClockWidget
from utils import ClockAngleUtils, TimeUtils

WORLD_CLOCK_CITIES: tuple[tuple[str, float], ...] = (
    ("Local", 0.0),
    ("New York", -4.0),
    ("Bogota", -5.0),
    ("London", 1.0),
    ("Dubai", 4.0),
    ("Delhi", 5.5),
    ("Tokyo", 9.0),
    ("Sydney", 10.0),
)

BUTTON_FG = "#e2e8f0"
BUTTON_HOVER = "#cbd5e1"
BUTTON_TEXT = "#0f172a"
BUTTON_BORDER = "#cbd5e1"
LOCAL_BUTTON_FG = "#0f172a"
LOCAL_BUTTON_HOVER = "#1e293b"
LOCAL_BUTTON_TEXT = "#f8fafc"


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


class ClockTab(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="transparent")

        self._update_job: str | None = None
        self._local_nav_job: str | None = None
        self._local_nav_direction = 0
        self._local_nav_steps_remaining = 0
        self._utc_now_provider = lambda: datetime.now(timezone.utc)
        self._carousel = WorldClockCarousel(self._build_city_dataset())
        self._hover_direction: int | None = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.clock_shell = ctk.CTkFrame(self, fg_color="transparent")
        self.clock_shell.grid(row=0, column=0, padx=1, pady=12, sticky="nsew")
        self.clock_shell.grid_rowconfigure(0, weight=1)
        self.clock_shell.grid_columnconfigure(0, weight=0)
        self.clock_shell.grid_columnconfigure(1, weight=2)
        self.clock_shell.grid_columnconfigure(2, weight=0)

        self.left_button = ctk.CTkButton(
            self.clock_shell,
            text="<",
            width=40,
            height=40,
            corner_radius=20,
            border_width=1,
            border_color=BUTTON_BORDER,
            fg_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            command=lambda: self._navigate(-1),
        )
        self.left_button.grid(row=0, column=0, padx=(6, 8), pady=0)

        self.clock = AnalogClockWidget(self.clock_shell)
        self.clock.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        self.right_button = ctk.CTkButton(
            self.clock_shell,
            text=">",
            width=40,
            height=40,
            corner_radius=20,
            border_width=1,
            border_color=BUTTON_BORDER,
            fg_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            command=lambda: self._navigate(1),
        )
        self.right_button.grid(row=0, column=2, padx=(8, 6), pady=0)

        self.left_button.bind("<Enter>", lambda _: self._on_arrow_hover(-1))
        self.left_button.bind("<Leave>", self._on_arrow_leave)
        self.right_button.bind("<Enter>", lambda _: self._on_arrow_hover(1))
        self.right_button.bind("<Leave>", self._on_arrow_leave)

        self.city_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#0f172a",
        )
        self.city_label.grid(row=1, column=0, padx=12, pady=(0, 2), sticky="ew")

        self.breadcrumb_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            text_color="#475569",
        )
        self.breadcrumb_label.grid(row=2, column=0, padx=5, pady=(0, 8), sticky="ew")

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
    def _angles_for_time(current_time: datetime) -> tuple[float, float, float]:
        return ClockAngleUtils.angles_for_datetime(current_time)

    def _render_active_city(self, *, animate: bool) -> None:
        utc_now = self._utc_now_provider()
        city = self._carousel.current
        city_time = self._city_time(city, utc_now)
        digital_time = TimeUtils.format_digital(city_time)

        self.city_label.configure(
            text=f"{city.city_name}  |  {_format_offset(city.timezone_offset)}"
        )

        prev_city = self._carousel.node_at_offset(-1)
        next_city = self._carousel.node_at_offset(1)
        self.breadcrumb_label.configure(
            text=(
                f"Prev: {prev_city.city_name} ({_format_offset(prev_city.timezone_offset)})"
                f"  |  Next: {next_city.city_name} ({_format_offset(next_city.timezone_offset)})"
            )
        )

        if animate:
            self.clock.animate_to_display(city_time, digital_text=digital_time)
        else:
            self.clock.set_display(city_time, digital_text=digital_time)

        self._sync_preview(utc_now)

    def _navigate(
        self,
        direction: int,
        *,
        cancel_local_nav: bool = True,
    ) -> None:
        if cancel_local_nav:
            self._cancel_local_navigation()

        if direction > 0:
            self._carousel.rotate_next(direction)
        else:
            self._carousel.rotate_prev(abs(direction))

        self._render_active_city(animate=True)

    def _cancel_local_navigation(self) -> None:
        SchedulerUtils.cancel_after_job(self, self._local_nav_job)
        self._local_nav_job = None
        self._local_nav_steps_remaining = 0
        self._local_nav_direction = 0

    def go_to_local(self) -> None:
        self._cancel_local_navigation()
        self._hover_direction = None
        self.clock.clear_preview()

        if not self._carousel.has_city("Local"):
            return

        offset = self._carousel.shortest_offset_to_city("Local")
        if offset == 0:
            return

        self._local_nav_direction = 1 if offset > 0 else -1
        self._local_nav_steps_remaining = abs(offset)
        self._run_local_navigation_step()

    def _run_local_navigation_step(self) -> None:
        self._local_nav_job = None
        if self._local_nav_steps_remaining <= 0 or self._local_nav_direction == 0:
            self._cancel_local_navigation()
            return

        self._navigate(self._local_nav_direction, cancel_local_nav=False)
        self._local_nav_steps_remaining -= 1

        if self._local_nav_steps_remaining > 0:
            self._local_nav_job = self.after(190, self._run_local_navigation_step)
        else:
            self._cancel_local_navigation()

    def on_shortcut_left(self) -> None:
        self._navigate(-1)

    def on_shortcut_right(self) -> None:
        self._navigate(1)

    def on_shortcut_local(self) -> None:
        self.go_to_local()

    def _on_arrow_hover(self, direction: int) -> None:
        self._hover_direction = direction
        self._sync_preview()

    def _on_arrow_leave(self, _event: object) -> None:
        self._hover_direction = None
        self.clock.clear_preview()

    def _sync_preview(self, utc_now: datetime | None = None) -> None:
        if self._hover_direction is None:
            self.clock.clear_preview()
            return

        now_utc = utc_now or self._utc_now_provider()
        preview_city = self._carousel.node_at_offset(self._hover_direction)
        preview_time = self._city_time(preview_city, now_utc)
        self.clock.set_preview_angles(self._angles_for_time(preview_time))


def build(parent: ctk.CTkFrame) -> ClockTab:
    return ClockTab(parent)
