from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import datetime, timedelta

import customtkinter as ctk

from core.AnalogClockBase import AnalogClockBase
from ui.helpers import ClockFaceDrawer, ClockHandDrawer, SchedulerUtils
from utils import ClockAngleUtils, TimeUtils

FACE_BG = "#f8fafc"
FACE_OUTLINE = "#0f172a"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#334155"
MAJOR_TICK = "#0f172a"
MINOR_TICK = "#94a3b8"
SECOND_HAND = "#0ea5e9"
PREVIEW_HAND = "#94a3b8"


class AnalogClockWidget(ctk.CTkFrame):
    def __init__(
        self,
        master: tk.Misc | ctk.CTkBaseClass,
        *,
        time_provider: Callable[[], datetime] | None = None,
        digital_formatter: Callable[[datetime], str] | None = None,
    ) -> None:
        super().__init__(master=master, fg_color=FACE_BG, corner_radius=16)

        self._redraw_job: str | None = None
        self._animation_job: str | None = None
        self._time_provider = time_provider or datetime.now
        self._digital_formatter = digital_formatter or TimeUtils.format_digital
        self._display_time = self._time_provider()
        self._override_angles: tuple[float, float, float] | None = None
        self._preview_angles: tuple[float, float, float] | None = None

        self._animation_step = 0
        self._animation_total_steps = 12
        self._animation_start_angles: tuple[float, float, float] | None = None
        self._animation_target_angles: tuple[float, float, float] | None = None
        self._animation_target_time: datetime | None = None
        self._animation_digital_text: str | None = None

        self.clock_base = AnalogClockBase()
        self._sync_to_current_time(self._display_time)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bg=FACE_BG,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.digital_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=TEXT_SECONDARY,
        )
        self.digital_label.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="ew")
        self.digital_label.configure(text=self._digital_formatter(self._display_time))

        self.after_idle(self._draw_clock)

    def destroy(self) -> None:
        self._cancel_job("_redraw_job")
        self._cancel_job("_animation_job")
        super().destroy()

    def _cancel_job(self, attribute_name: str) -> None:
        job = getattr(self, attribute_name)
        SchedulerUtils.cancel_after_job(self, job)
        setattr(self, attribute_name, None)

    def set_display(
        self, current_time: datetime, digital_text: str | None = None
    ) -> None:
        self._cancel_job("_animation_job")
        self._override_angles = None
        self._display_time = current_time
        self._sync_to_current_time(current_time)

        if digital_text is None:
            digital_text = self._digital_formatter(current_time)

        self.digital_label.configure(text=digital_text)
        self._draw_clock()

    def animate_to_display(
        self,
        current_time: datetime,
        digital_text: str | None = None,
    ) -> None:
        self._cancel_job("_animation_job")

        if digital_text is None:
            digital_text = self._digital_formatter(current_time)

        self.digital_label.configure(text=digital_text)
        self._animation_target_time = current_time
        self._animation_digital_text = digital_text
        self._animation_start_angles = self._override_angles or self._base_angles()
        self._animation_target_angles = ClockAngleUtils.angles_for_datetime(
            current_time
        )
        self._animation_step = 0
        self._run_animation_frame()

    def set_preview_angles(
        self, preview_angles: tuple[float, float, float] | None
    ) -> None:
        if preview_angles is None:
            self._preview_angles = None
        else:
            self._preview_angles = (
                preview_angles[0] % 360.0,
                preview_angles[1] % 360.0,
                preview_angles[2] % 360.0,
            )
        self._draw_clock()

    def clear_preview(self) -> None:
        self.set_preview_angles(None)

    def tick(self) -> None:
        self.set_display(self._display_time + timedelta(seconds=1))

    def _sync_to_current_time(self, current_time: datetime) -> None:
        self.clock_base.sync_time(
            current_time.hour,
            current_time.minute,
            current_time.second,
        )

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self._cancel_job("_redraw_job")
        self._redraw_job = self.after_idle(self._draw_clock)

    def _run_animation_frame(self) -> None:
        if (
            self._animation_start_angles is None
            or self._animation_target_angles is None
        ):
            return

        self._animation_step += 1
        progress = min(self._animation_step / self._animation_total_steps, 1.0)
        eased_progress = 1.0 - (1.0 - progress) ** 2

        self._override_angles = (
            self._interpolate_angle(
                self._animation_start_angles[0],
                self._animation_target_angles[0],
                eased_progress,
            ),
            self._interpolate_angle(
                self._animation_start_angles[1],
                self._animation_target_angles[1],
                eased_progress,
            ),
            self._interpolate_angle(
                self._animation_start_angles[2],
                self._animation_target_angles[2],
                eased_progress,
            ),
        )
        self._draw_clock()

        if progress < 1.0:
            self._animation_job = self.after(16, self._run_animation_frame)
            return

        target_time = self._animation_target_time
        digital_text = self._animation_digital_text

        self._animation_job = None
        self._override_angles = None

        if target_time is not None:
            self.set_display(target_time, digital_text=digital_text)

    @staticmethod
    def _interpolate_angle(start: float, target: float, progress: float) -> float:
        shortest = ((target - start + 180.0) % 360.0) - 180.0
        return start + shortest * progress

    def _base_angles(self) -> tuple[float, float, float]:
        hour_value = self.clock_base.hour_position % 12
        minute_value = self.clock_base.minute_position
        second_value = self.clock_base.second_position
        return ClockAngleUtils.angles_for_positions(
            hour_value=hour_value,
            minute_value=minute_value,
            second_value=second_value,
        )

    def _draw_clock(self) -> None:
        self._redraw_job = None
        self.canvas.delete("all")

        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        if width <= 1 or height <= 1:
            return

        size = min(width, height) * 0.95
        center_x = width / 2
        center_y = height / 2
        radius = size * 0.42
        ClockFaceDrawer.draw_face(
            self.canvas,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            size=size,
            face_bg=FACE_BG,
            face_outline=FACE_OUTLINE,
            text_primary=TEXT_PRIMARY,
            major_tick_color=MAJOR_TICK,
            minor_tick_color=MINOR_TICK,
        )

        self._draw_preview_hands(center_x, center_y, radius, size)
        self._draw_hands(center_x, center_y, radius, size)

    def _draw_preview_hands(
        self,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
    ) -> None:
        if self._preview_angles is None:
            return
        ClockHandDrawer.draw_preview_hands(
            self.canvas,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            size=size,
            angles=self._preview_angles,
            color=PREVIEW_HAND,
        )

    def _draw_hands(
        self,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
    ) -> None:
        if self._override_angles is None:
            angles = self._base_angles()
        else:
            angles = self._override_angles

        ClockHandDrawer.draw_primary_hands(
            self.canvas,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            size=size,
            angles=angles,
            text_primary=TEXT_PRIMARY,
            second_hand=SECOND_HAND,
        )
