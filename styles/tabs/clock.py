from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from styles.widgets import AnalogClockWidget


class ClockTab(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="transparent")

        self._update_job: str | None = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.clock = AnalogClockWidget(self)
        self.clock.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        self._tick()

    def destroy(self) -> None:
        if self._update_job is not None:
            try:
                self.after_cancel(self._update_job)
            except Exception:
                pass
            self._update_job = None
        super().destroy()

    def _tick(self) -> None:
        now = datetime.now()
        self.clock.set_display(now)
        self._update_job = self.after(1000, self._tick)


def build(parent: ctk.CTkFrame) -> ctk.CTkFrame:
    return ClockTab(parent)
