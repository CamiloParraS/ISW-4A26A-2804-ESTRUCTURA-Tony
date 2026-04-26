from __future__ import annotations

import tkinter as tk

from utils import GeometryUtils


class ClockHandDrawer:
    @staticmethod
    def draw_preview_hands(
        canvas: tk.Canvas,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
        angles: tuple[float, float, float],
        color: str,
    ) -> None:
        hour_angle, minute_angle, second_angle = angles
        for angle, length, width in [
            (hour_angle, radius * 0.48, max(int(size * 0.012), 3)),
            (minute_angle, radius * 0.68, max(int(size * 0.009), 2)),
            (second_angle, radius * 0.82, max(int(size * 0.004), 1)),
        ]:
            end_x, end_y = GeometryUtils.polar_to_cartesian(
                center_x, center_y, length, angle
            )
            canvas.create_line(
                center_x,
                center_y,
                end_x,
                end_y,
                fill=color,
                width=width,
                capstyle="round",
                dash=(4, 4),
            )

    @staticmethod
    def draw_primary_hands(
        canvas: tk.Canvas,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
        angles: tuple[float, float, float],
        text_primary: str,
        second_hand: str,
    ) -> None:
        hour_angle, minute_angle, second_angle = angles

        shadow_offset = max(1, size * 0.005)
        for angle, length, width, color in [
            (hour_angle, radius * 0.48, max(int(size * 0.018), 5), "#cbd5e1"),
            (minute_angle, radius * 0.68, max(int(size * 0.012), 4), "#cbd5e1"),
            (second_angle, radius * 0.82, max(int(size * 0.006), 2), "#cbd5e1"),
        ]:
            end_x, end_y = GeometryUtils.polar_to_cartesian(
                center_x, center_y, length, angle
            )
            canvas.create_line(
                center_x + shadow_offset,
                center_y + shadow_offset,
                end_x + shadow_offset,
                end_y + shadow_offset,
                fill=color,
                width=width,
                capstyle="round",
            )

        hour_end = GeometryUtils.polar_to_cartesian(
            center_x, center_y, radius * 0.48, hour_angle
        )
        minute_end = GeometryUtils.polar_to_cartesian(
            center_x, center_y, radius * 0.68, minute_angle
        )
        second_end = GeometryUtils.polar_to_cartesian(
            center_x, center_y, radius * 0.82, second_angle
        )

        canvas.create_line(
            center_x,
            center_y,
            *hour_end,
            fill=text_primary,
            width=max(int(size * 0.018), 5),
            capstyle="round",
        )
        canvas.create_line(
            center_x,
            center_y,
            *minute_end,
            fill=text_primary,
            width=max(int(size * 0.012), 4),
            capstyle="round",
        )
        canvas.create_line(
            center_x,
            center_y,
            *second_end,
            fill=second_hand,
            width=max(int(size * 0.006), 2),
            capstyle="round",
        )

        canvas.create_oval(
            center_x - 8,
            center_y - 8,
            center_x + 8,
            center_y + 8,
            fill=text_primary,
            outline="",
        )
