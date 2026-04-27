from __future__ import annotations

import tkinter as tk

from utils import ClockAngles, GeometryUtils

HOUR_HAND_LENGTH_RATIO = 0.48
MINUTE_HAND_LENGTH_RATIO = 0.68
SECOND_HAND_LENGTH_RATIO = 0.82

PREVIEW_HOUR_WIDTH_RATIO = 0.012
PREVIEW_MINUTE_WIDTH_RATIO = 0.009
PREVIEW_SECOND_WIDTH_RATIO = 0.004
PREVIEW_MIN_HOUR_WIDTH = 3
PREVIEW_MIN_MINUTE_WIDTH = 2
PREVIEW_MIN_SECOND_WIDTH = 1

PRIMARY_HOUR_WIDTH_RATIO = 0.018
PRIMARY_MINUTE_WIDTH_RATIO = 0.012
PRIMARY_SECOND_WIDTH_RATIO = 0.006
PRIMARY_MIN_HOUR_WIDTH = 5
PRIMARY_MIN_MINUTE_WIDTH = 4
PRIMARY_MIN_SECOND_WIDTH = 2

SHADOW_COLOR = "#cbd5e1"
SHADOW_OFFSET_RATIO = 0.005
MIN_SHADOW_OFFSET = 1
CENTER_CAP_RADIUS = 8
DASH_PATTERN = (4, 4)


class ClockHandDrawer:
    @staticmethod
    def draw_preview_hands(
        canvas: tk.Canvas,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
        angles: ClockAngles,
        color: str,
    ) -> None:
        hour_angle, minute_angle, second_angle = angles
        for angle, length, width in [
            (
                hour_angle,
                radius * HOUR_HAND_LENGTH_RATIO,
                max(int(size * PREVIEW_HOUR_WIDTH_RATIO), PREVIEW_MIN_HOUR_WIDTH),
            ),
            (
                minute_angle,
                radius * MINUTE_HAND_LENGTH_RATIO,
                max(
                    int(size * PREVIEW_MINUTE_WIDTH_RATIO),
                    PREVIEW_MIN_MINUTE_WIDTH,
                ),
            ),
            (
                second_angle,
                radius * SECOND_HAND_LENGTH_RATIO,
                max(int(size * PREVIEW_SECOND_WIDTH_RATIO), PREVIEW_MIN_SECOND_WIDTH),
            ),
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
                dash=DASH_PATTERN,
            )

    @staticmethod
    def draw_primary_hands(
        canvas: tk.Canvas,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        size: float,
        angles: ClockAngles,
        text_primary: str,
        second_hand: str,
    ) -> None:
        hour_angle, minute_angle, second_angle = angles

        shadow_offset = max(MIN_SHADOW_OFFSET, size * SHADOW_OFFSET_RATIO)
        for angle, length, width, color in [
            (
                hour_angle,
                radius * HOUR_HAND_LENGTH_RATIO,
                max(int(size * PRIMARY_HOUR_WIDTH_RATIO), PRIMARY_MIN_HOUR_WIDTH),
                SHADOW_COLOR,
            ),
            (
                minute_angle,
                radius * MINUTE_HAND_LENGTH_RATIO,
                max(int(size * PRIMARY_MINUTE_WIDTH_RATIO), PRIMARY_MIN_MINUTE_WIDTH),
                SHADOW_COLOR,
            ),
            (
                second_angle,
                radius * SECOND_HAND_LENGTH_RATIO,
                max(int(size * PRIMARY_SECOND_WIDTH_RATIO), PRIMARY_MIN_SECOND_WIDTH),
                SHADOW_COLOR,
            ),
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
            center_x, center_y, radius * HOUR_HAND_LENGTH_RATIO, hour_angle
        )
        minute_end = GeometryUtils.polar_to_cartesian(
            center_x, center_y, radius * MINUTE_HAND_LENGTH_RATIO, minute_angle
        )
        second_end = GeometryUtils.polar_to_cartesian(
            center_x, center_y, radius * SECOND_HAND_LENGTH_RATIO, second_angle
        )

        canvas.create_line(
            center_x,
            center_y,
            *hour_end,
            fill=text_primary,
            width=max(int(size * PRIMARY_HOUR_WIDTH_RATIO), PRIMARY_MIN_HOUR_WIDTH),
            capstyle="round",
        )
        canvas.create_line(
            center_x,
            center_y,
            *minute_end,
            fill=text_primary,
            width=max(
                int(size * PRIMARY_MINUTE_WIDTH_RATIO),
                PRIMARY_MIN_MINUTE_WIDTH,
            ),
            capstyle="round",
        )
        canvas.create_line(
            center_x,
            center_y,
            *second_end,
            fill=second_hand,
            width=max(int(size * PRIMARY_SECOND_WIDTH_RATIO), PRIMARY_MIN_SECOND_WIDTH),
            capstyle="round",
        )

        canvas.create_oval(
            center_x - CENTER_CAP_RADIUS,
            center_y - CENTER_CAP_RADIUS,
            center_x + CENTER_CAP_RADIUS,
            center_y + CENTER_CAP_RADIUS,
            fill=text_primary,
            outline="",
        )
