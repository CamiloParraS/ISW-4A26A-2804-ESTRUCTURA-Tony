from __future__ import annotations

import customtkinter as ctk

from ui.widgets import AnalogClockWidget

BUTTON_FG = "#e2e8f0"
BUTTON_HOVER = "#cbd5e1"
BUTTON_TEXT = "#0f172a"
BUTTON_BORDER = "#cbd5e1"


class ClockTabUiMixin:
    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.clock_shell = ctk.CTkFrame(self, fg_color="transparent")
        self.clock_shell.grid(row=0, column=0, padx=1, pady=12, sticky="nsew")
        self.clock_shell.grid_rowconfigure(0, weight=1)
        self.clock_shell.grid_columnconfigure(0, weight=0)
        self.clock_shell.grid_columnconfigure(1, weight=2)
        self.clock_shell.grid_columnconfigure(2, weight=0)

        self.left_button = ctk.CTkButton(
            self.clock_shell,
            text="<",
            width=40,
            height=40,
            corner_radius=20,
            border_width=1,
            border_color=BUTTON_BORDER,
            fg_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            command=lambda: self._navigate(-1),
        )
        self.left_button.grid(row=0, column=0, padx=(6, 8), pady=0)

        self.clock = AnalogClockWidget(self.clock_shell)
        self.clock.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        self.right_button = ctk.CTkButton(
            self.clock_shell,
            text=">",
            width=40,
            height=40,
            corner_radius=20,
            border_width=1,
            border_color=BUTTON_BORDER,
            fg_color=BUTTON_FG,
            hover_color=BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            command=lambda: self._navigate(1),
        )
        self.right_button.grid(row=0, column=2, padx=(8, 6), pady=0)

        self.left_button.bind("<Enter>", lambda _: self._on_arrow_hover(-1))
        self.left_button.bind("<Leave>", self._on_arrow_leave)
        self.right_button.bind("<Enter>", lambda _: self._on_arrow_hover(1))
        self.right_button.bind("<Leave>", self._on_arrow_leave)

        self.city_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#0f172a",
        )
        self.city_label.grid(row=1, column=0, padx=12, pady=(0, 2), sticky="ew")

        self.breadcrumb_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            text_color="#475569",
        )
        self.breadcrumb_label.grid(row=2, column=0, padx=5, pady=(0, 8), sticky="ew")
