from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from ui.helpers import SchedulerUtils

from .countdown_state import CountdownStateMixin
from .countdown_ui import CountdownUiMixin


class CountdownTab(CountdownStateMixin, CountdownUiMixin, ctk.CTkFrame):
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

        self._build_layout()
        self._refresh_view()
        self._schedule_tick()

    def destroy(self) -> None:
        SchedulerUtils.cancel_after_job(self, self._tick_job)
        self._tick_job = None
        super().destroy()

    def _on_input_focus_out(self, event: tk.Event) -> None:
        self._on_input_commit(event)

    def _on_input_commit(self, event: tk.Event | None = None) -> None:
        if self._normalizing_inputs or self._state == "running":
            return

        hours, minutes, seconds = self._normalize_fields()
        self._remaining_seconds = hours * 3600 + minutes * 60 + seconds

        if self._state == "paused":
            self._deadline = None

        self._refresh_view()

    def _schedule_tick(self) -> None:
        self._tick_job = self.after(200, self._tick)


def build(parent: ctk.CTkFrame) -> ctk.CTkFrame:
    return CountdownTab(parent)
