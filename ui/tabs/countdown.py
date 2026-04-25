from __future__ import annotations

import math
import time
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

from ui.widgets import AnalogClockWidget
from utils import TimeUtils, ValidationUtils


class CountdownTab(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="transparent")

        self._state = "ready"
        self._deadline: float | None = None
        self._remaining_seconds = 60
        self._tick_job: str | None = None
        self._normalizing_inputs = False

        self._hours_var = tk.StringVar(value="00")
        self._minutes_var = tk.StringVar(value="01")
        self._seconds_var = tk.StringVar(value="00")
        self._status_var = tk.StringVar(value="Ready")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.clock = AnalogClockWidget(self)
        self.clock.grid(row=0, column=0, padx=8, pady=(8, 6), sticky="nsew")

        self.controls = ctk.CTkFrame(self, corner_radius=14)
        self.controls.grid(row=1, column=0, padx=8, pady=(6, 8), sticky="ew")
        self.controls.grid_columnconfigure(0, weight=1)
        self.controls.grid_columnconfigure(1, weight=1)
        self.controls.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            self.controls,
            text="Countdown",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=(12, 10), sticky="w")

        selectors = ctk.CTkFrame(self.controls, fg_color="transparent")
        selectors.grid(
            row=1, column=0, columnspan=3, padx=12, pady=(0, 10), sticky="ew"
        )
        selectors.grid_columnconfigure(0, weight=1)
        selectors.grid_columnconfigure(1, weight=1)
        selectors.grid_columnconfigure(2, weight=1)

        self._hours_entry = self._build_entry_cell(
            selectors,
            column=0,
            label="Hours",
            variable=self._hours_var,
        )
        self._minutes_entry = self._build_entry_cell(
            selectors,
            column=1,
            label="Minutes",
            variable=self._minutes_var,
        )
        self._seconds_entry = self._build_entry_cell(
            selectors,
            column=2,
            label="Seconds",
            variable=self._seconds_var,
        )

        buttons = ctk.CTkFrame(self.controls, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=3, padx=12, pady=(2, 0), sticky="ew")
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
        ).grid(row=3, column=0, columnspan=3, padx=12, pady=(12, 12), sticky="w")

        for entry in (self._hours_entry, self._minutes_entry, self._seconds_entry):
            entry.bind("<FocusOut>", self._on_input_focus_out)
            entry.bind("<Return>", self._on_input_commit)

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

    def _build_entry_cell(
        self,
        parent: ctk.CTkFrame,
        column: int,
        label: str,
        variable: tk.StringVar,
    ) -> ctk.CTkEntry:
        cell = ctk.CTkFrame(parent)
        cell.grid(
            row=0,
            column=column,
            padx=(0, 8) if column < 2 else (0, 0),
            pady=0,
            sticky="ew",
        )
        cell.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(cell, text=label, anchor="w").grid(
            row=0,
            column=0,
            padx=10,
            pady=(8, 6),
            sticky="w",
        )

        vcmd = self.register(ValidationUtils.is_digits_only)
        entry = ctk.CTkEntry(
            cell,
            textvariable=variable,
            justify="center",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            validate="key",
            validatecommand=(vcmd, "%P"),
        )
        entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        return entry

    def _normalize_fields(self) -> tuple[int, int, int]:
        h = ValidationUtils.safe_int(self._hours_var.get())
        m = ValidationUtils.safe_int(self._minutes_var.get())
        s = ValidationUtils.safe_int(self._seconds_var.get())

        hours, minutes, seconds = TimeUtils.normalize_time(h, m, s)

        self._normalizing_inputs = True
        try:
            self._hours_var.set(str(hours) if hours >= 100 else f"{hours:02}")
            self._minutes_var.set(f"{minutes:02}")
            self._seconds_var.set(f"{seconds:02}")
        finally:
            self._normalizing_inputs = False

        return hours, minutes, seconds

    def _on_input_focus_out(self, event: tk.Event) -> None:
        self._on_input_commit(event)

    def _on_input_commit(self, event: tk.Event | None = None) -> None:
        if self._normalizing_inputs or self._state == "running":
            return

        hours, minutes, seconds = self._normalize_fields()
        self._remaining_seconds = TimeUtils.to_seconds(hours, minutes, seconds)

        if self._state == "paused":
            self._deadline = None

        self._refresh_view()

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
        hours, minutes, seconds = self._normalize_fields()
        return max(1, TimeUtils.to_seconds(hours, minutes, seconds))

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

        input_state = "disabled" if self._state == "running" else "normal"
        text_col = "#9CA3AF" if self._state == "running" else "#000000"
        
        self._hours_entry.configure(state=input_state, text_color=text_col)
        self._minutes_entry.configure(state=input_state, text_color=text_col)
        self._seconds_entry.configure(state=input_state, text_color=text_col)

        hours, minutes, seconds = TimeUtils.from_seconds(self._remaining_seconds)

        digital = f"{hours:02}:{minutes:02}:{seconds:02}"
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
