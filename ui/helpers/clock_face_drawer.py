from __future__ import annotations

import math
import tkinter as tk

TICK_OUTER_RATIO = 0.98
MAJOR_TICK_RATIO = 0.06
MINOR_TICK_RATIO = 0.03
NUMBER_RADIUS_RATIO = 0.78
OUTLINE_WIDTH_RATIO = 0.012
MIN_OUTLINE_WIDTH = 2
MAJOR_TICK_WIDTH_RATIO = 0.008
MIN_MAJOR_TICK_WIDTH = 1
MIN_MAJOR_TICK_LENGTH = 10
MIN_MINOR_TICK_LENGTH = 6
CENTER_DOT_RADIUS = 7
NUMBER_FONT_FAMILY = "Segoe UI"
NUMBER_FONT_SIZE = 18
NUMBER_FONT_WEIGHT = "bold"


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
        tick_outer = radius * TICK_OUTER_RATIO
        major_tick = max(size * MAJOR_TICK_RATIO, MIN_MAJOR_TICK_LENGTH)
        minor_tick = max(size * MINOR_TICK_RATIO, MIN_MINOR_TICK_LENGTH)
        number_radius = radius * NUMBER_RADIUS_RATIO

        canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=face_bg,
            outline=face_outline,
            width=max(int(size * OUTLINE_WIDTH_RATIO), MIN_OUTLINE_WIDTH),
        )

        canvas.create_oval(
            center_x - CENTER_DOT_RADIUS,
            center_y - CENTER_DOT_RADIUS,
            center_x + CENTER_DOT_RADIUS,
            center_y + CENTER_DOT_RADIUS,
            fill=text_primary,
            outline="",
        )

        for mark in range(60):
            angle = math.radians(mark * 6 - 90)
            inner = tick_outer - (major_tick if mark % 5 == 0 else minor_tick)
            tick_width = (
                max(int(size * MAJOR_TICK_WIDTH_RATIO), MIN_MAJOR_TICK_WIDTH)
                if mark % 5 == 0
                else 1
            )
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
                font=(NUMBER_FONT_FAMILY, NUMBER_FONT_SIZE, NUMBER_FONT_WEIGHT),
            )
