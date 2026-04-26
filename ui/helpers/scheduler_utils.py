from __future__ import annotations

import tkinter as tk


class SchedulerUtils:
    @staticmethod
    def cancel_after_job(widget: tk.Misc, job_id: str | None) -> None:
        if job_id is None:
            return
        try:
            widget.after_cancel(job_id)
        except tk.TclError:
            pass
