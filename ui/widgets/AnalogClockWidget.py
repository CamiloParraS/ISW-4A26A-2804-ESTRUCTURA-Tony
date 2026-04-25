from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable
from datetime import datetime

import customtkinter as ctk

from core.AnalogClockBase import AnalogClockBase
from utils import GeometryUtils, TimeUtils

FACE_BG = "#f8fafc"
FACE_OUTLINE = "#0f172a"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#334155"
MAJOR_TICK = "#0f172a"
MINOR_TICK = "#94a3b8"
SECOND_HAND = "#0ea5e9"


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
        self._time_provider = time_provider or datetime.now
        self._digital_formatter = digital_formatter or TimeUtils.format_digital
        self._display_time = self._time_provider()

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
        super().destroy()

    def _cancel_job(self, attribute_name: str) -> None:
        job = getattr(self, attribute_name)
        if job is not None:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
            finally:
                setattr(self, attribute_name, None)

    def set_display(
        self, current_time: datetime, digital_text: str | None = None
    ) -> None:
        self._display_time = current_time
        self._sync_to_current_time(current_time)

        if digital_text is None:
            digital_text = self._digital_formatter(current_time)

        self.digital_label.configure(text=digital_text)
        self._draw_clock()

    def tick(self) -> None:
        self.clock_base.tick()
        
        from datetime import timedelta
        self._display_time += timedelta(seconds=1)
        
        digital_text = self._digital_formatter(self._display_time)
        self.digital_label.configure(text=digital_text)
        
        self._draw_clock()

    def _sync_to_current_time(self, current_time: datetime) -> None:
        self.clock_base.sync_time(
            current_time.hour, current_time.minute, current_time.second
        )

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self._cancel_job("_redraw_job")
        self._redraw_job = self.after_idle(self._draw_clock)

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
        tick_outer = radius * 0.98
        major_tick = max(size * 0.06, 10)
        minor_tick = max(size * 0.03, 6)
        number_radius = radius * 0.78

        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=FACE_BG,
            outline=FACE_OUTLINE,
            width=max(int(size * 0.012), 2),
        )

        self.canvas.create_oval(
            center_x - 7,
            center_y - 7,
            center_x + 7,
            center_y + 7,
            fill=TEXT_PRIMARY,
            outline="",
        )

        for mark in range(60):
            angle = math.radians(mark * 6 - 90)
            inner = tick_outer - (major_tick if mark % 5 == 0 else minor_tick)
            tick_width = max(int(size * 0.008), 1) if mark % 5 == 0 else 1
            color = MAJOR_TICK if mark % 5 == 0 else MINOR_TICK
            x_outer = center_x + tick_outer * math.cos(angle)
            y_outer = center_y + tick_outer * math.sin(angle)
            x_inner = center_x + inner * math.cos(angle)
            y_inner = center_y + inner * math.sin(angle)
            self.canvas.create_line(
                x_inner,
                y_inner,
                x_outer,
                y_outer,
                fill=color,
                width=tick_width,
            )

        for number in range(1, 13):
            angle = math.radians(number * 30 - 90)
            x = center_x + number_radius * math.cos(angle)
            y = center_y + number_radius * math.sin(angle)
            self.canvas.create_text(
                x,
                y,
                text=str(number),
                fill=TEXT_PRIMARY,
                font=("Segoe UI", 18, "bold"),
            )

        self._draw_hands(center_x, center_y, radius, size)

    def _draw_hands(
        self,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
    ) -> None:
        hour_value = self.clock_base.hour_position
        minute_value = self.clock_base.minute_position
        second_value = self.clock_base.second_position

        hour_angle = (
            (hour_value % 12) * 30
            + (minute_value / 60.0) * 30
            + (second_value / 3600.0) * 30
        )
        minute_angle = minute_value * 6 + second_value * 0.1
        second_angle = second_value * 6

        # Draw shadows for depth
        shadow_offset = max(1, size * 0.005)
        for angle, length, width, color in [
            (hour_angle, radius * 0.48, max(int(size * 0.018), 5), "#cbd5e1"),
            (minute_angle, radius * 0.68, max(int(size * 0.012), 4), "#cbd5e1"),
            (second_angle, radius * 0.82, max(int(size * 0.006), 2), "#cbd5e1"),
        ]:
            end_x, end_y = GeometryUtils.polar_to_cartesian(center_x, center_y, length, angle)
            self.canvas.create_line(
                center_x + shadow_offset,
                center_y + shadow_offset,
                end_x + shadow_offset,
                end_y + shadow_offset,
                fill=color,
                width=width,
                capstyle="round",
                tags="hands",
            )

        hour_end = GeometryUtils.polar_to_cartesian(center_x, center_y, radius * 0.48, hour_angle)
        minute_end = GeometryUtils.polar_to_cartesian(center_x, center_y, radius * 0.68, minute_angle)
        second_end = GeometryUtils.polar_to_cartesian(center_x, center_y, radius * 0.82, second_angle)

        self.canvas.delete("hands")
        self.canvas.create_line(
            center_x,
            center_y,
            *hour_end,
            fill=TEXT_PRIMARY,
            width=max(int(size * 0.018), 5),
            capstyle="round",
            tags="hands",
        )
        self.canvas.create_line(
            center_x,
            center_y,
            *minute_end,
            fill=TEXT_PRIMARY,
            width=max(int(size * 0.012), 4),
            capstyle="round",
            tags="hands",
        )
        self.canvas.create_line(
            center_x,
            center_y,
            *second_end,
            fill=SECOND_HAND,
            width=max(int(size * 0.006), 2),
            capstyle="round",
            tags="hands",
        )

        self.canvas.create_oval(
            center_x - 8,
            center_y - 8,
            center_x + 8,
            center_y + 8,
            fill=TEXT_PRIMARY,
            outline="",
            tags="hands",
        )
