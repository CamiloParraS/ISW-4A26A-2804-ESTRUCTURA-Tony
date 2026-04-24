from __future__ import annotations

import math
import time
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

from styles.widgets import AnalogClockWidget


class CountdownTab(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="transparent")

        self._state = "ready"
        self._deadline: float | None = None
        self._remaining_seconds = 60
        self._tick_job: str | None = None

        self._hours_var = tk.StringVar(value="00")
        self._minutes_var = tk.StringVar(value="01")
        self._seconds_var = tk.StringVar(value="00")
        self._status_var = tk.StringVar(value="Ready")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.clock = AnalogClockWidget(self)
        self.clock.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="nsew")

        self.controls = ctk.CTkFrame(self, corner_radius=14)
        self.controls.grid(row=0, column=1, padx=(8, 12), pady=12, sticky="ns")
        self.controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.controls,
            text="Countdown",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 10), sticky="w")

        self._hours_entry = self._build_entry_row(1, "Hours", self._hours_var)
        self._minutes_entry = self._build_entry_row(2, "Minutes", self._minutes_var)
        self._seconds_entry = self._build_entry_row(3, "Seconds", self._seconds_var)

        buttons = ctk.CTkFrame(self.controls, fg_color="transparent")
        buttons.grid(row=4, column=0, columnspan=2, padx=12, pady=(12, 0), sticky="ew")
        for index in range(4):
            buttons.grid_columnconfigure(index, weight=1)

        self.start_button = ctk.CTkButton(buttons, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="ew")

        self.pause_button = ctk.CTkButton(buttons, text="Pause", command=self.pause)
        self.pause_button.grid(row=0, column=1, padx=6, pady=0, sticky="ew")

        self.resume_button = ctk.CTkButton(buttons, text="Resume", command=self.resume)
        self.resume_button.grid(row=0, column=2, padx=6, pady=0, sticky="ew")

        self.reset_button = ctk.CTkButton(buttons, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=3, padx=(6, 0), pady=0, sticky="ew")

        ctk.CTkLabel(
            self.controls,
            textvariable=self._status_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#334155",
        ).grid(row=5, column=0, columnspan=2, padx=12, pady=(12, 12), sticky="w")

        self._refresh_view()
        self._schedule_tick()

    def destroy(self) -> None:
        if self._tick_job is not None:
            try:
                self.after_cancel(self._tick_job)
            except Exception:
                pass
            self._tick_job = None
        super().destroy()

    def _build_entry_row(
        self,
        row: int,
        label: str,
        variable: tk.StringVar,
    ) -> ctk.CTkEntry:
        ctk.CTkLabel(self.controls, text=label).grid(
            row=row,
            column=0,
            padx=12,
            pady=(0, 8),
            sticky="w",
        )
        entry = ctk.CTkEntry(
            self.controls, width=88, textvariable=variable, justify="center"
        )
        entry.grid(row=row, column=1, padx=(0, 12), pady=(0, 8), sticky="e")
        return entry

    def _schedule_tick(self) -> None:
        self._tick_job = self.after(200, self._tick)

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
        try:
            hours = int(self._hours_var.get())
            minutes = int(self._minutes_var.get())
            seconds = int(self._seconds_var.get())
        except ValueError:
            hours, minutes, seconds = 0, 1, 0

        hours = max(0, min(hours, 99))
        minutes = max(0, min(minutes, 59))
        seconds = max(0, min(seconds, 59))

        self._hours_var.set(f"{hours:02}")
        self._minutes_var.set(f"{minutes:02}")
        self._seconds_var.set(f"{seconds:02}")

        duration = hours * 3600 + minutes * 60 + seconds
        return max(1, duration)

    def _refresh_view(self) -> None:
        state_text = {
            "ready": "Ready",
            "running": "Running",
            "paused": "Paused",
            "finished": "Finished",
        }[self._state]
        self._status_var.set(state_text)

        self.start_button.configure(
            state="disabled" if self._state == "running" else "normal"
        )
        self.pause_button.configure(
            state="normal" if self._state == "running" else "disabled"
        )
        self.resume_button.configure(
            state="normal" if self._state == "paused" else "disabled"
        )

        total = self._remaining_seconds
        hours, rem = divmod(total, 3600)
        minutes, seconds = divmod(rem, 60)

        digital = (
            f"{hours:02}:{minutes:02}:{seconds:02}"
            if hours
            else f"{minutes:02}:{seconds:02}"
        )
        display_hour = hours % 12 or 12
        display_time = datetime(2000, 1, 1, display_hour, minutes, seconds)
        self.clock.set_display(display_time, digital_text=digital)

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


def build(parent: ctk.CTkFrame) -> ctk.CTkFrame:
    return CountdownTab(parent)
