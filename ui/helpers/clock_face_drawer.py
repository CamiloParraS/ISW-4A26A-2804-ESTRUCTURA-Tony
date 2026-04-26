from __future__ import annotations

import math
import tkinter as tk


class ClockFaceDrawer:
    @staticmethod
    def draw_face(
        canvas: tk.Canvas,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
        face_bg: str,
        face_outline: str,
        text_primary: str,
        major_tick_color: str,
        minor_tick_color: str,
    ) -> None:
        tick_outer = radius * 0.98
        major_tick = max(size * 0.06, 10)
        minor_tick = max(size * 0.03, 6)
        number_radius = radius * 0.78

        canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=face_bg,
            outline=face_outline,
            width=max(int(size * 0.012), 2),
        )

        canvas.create_oval(
            center_x - 7,
            center_y - 7,
            center_x + 7,
            center_y + 7,
            fill=text_primary,
            outline="",
        )

        for mark in range(60):
            angle = math.radians(mark * 6 - 90)
            inner = tick_outer - (major_tick if mark % 5 == 0 else minor_tick)
            tick_width = max(int(size * 0.008), 1) if mark % 5 == 0 else 1
            color = major_tick_color if mark % 5 == 0 else minor_tick_color
            x_outer = center_x + tick_outer * math.cos(angle)
            y_outer = center_y + tick_outer * math.sin(angle)
            x_inner = center_x + inner * math.cos(angle)
            y_inner = center_y + inner * math.sin(angle)
            canvas.create_line(
                x_inner,
                y_inner,
                x_outer,
                y_outer,
                fill=color,
                width=tick_width,
            )

        for number in range(1, 13):
            angle = math.radians(number * 30 - 90)
            x_pos = center_x + number_radius * math.cos(angle)
            y_pos = center_y + number_radius * math.sin(angle)
            canvas.create_text(
                x_pos,
                y_pos,
                text=str(number),
                fill=text_primary,
                font=("Segoe UI", 18, "bold"),
            )
