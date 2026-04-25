from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from ui.widgets import AnalogClockWidget


class ClockTab(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="transparent")

        self._update_job: str | None = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.clock = AnalogClockWidget(self)
        self.clock.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        self.clock.set_display(datetime.now())
        self._schedule_tick()

    def destroy(self) -> None:
        if self._update_job is not None:
            try:
                self.after_cancel(self._update_job)
            except Exception:
                pass
            self._update_job = None
        super().destroy()

    def _schedule_tick(self) -> None:
        now = datetime.now()
        delay_ms = max(25, 1000 - (now.microsecond // 1000))
        self._update_job = self.after(delay_ms, self._tick)

    def _tick(self) -> None:
        self.clock.tick()
        self._schedule_tick()


def build(parent: ctk.CTkFrame) -> ctk.CTkFrame:
    return ClockTab(parent)
