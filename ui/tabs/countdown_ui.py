from __future__ import annotations

import tkinter as tk
from datetime import datetime

import customtkinter as ctk

from ui.widgets import AnalogClockWidget
from utils import TimeUtils, ValidationUtils


class CountdownUiMixin:
    def _build_layout(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)

        self.read_panel = ctk.CTkFrame(self, corner_radius=18)
        self.read_panel.grid(row=0, column=0, padx=(8, 4), pady=8, sticky="nsew")
        self.read_panel.grid_rowconfigure(0, weight=1)
        self.read_panel.grid_rowconfigure(1, weight=0)
        self.read_panel.grid_columnconfigure(0, weight=1)

        self.clock = AnalogClockWidget(self.read_panel)
        self.clock.digital_label.configure(
            font=ctk.CTkFont(family="Consolas", size=34, weight="bold"),
            text_color="#0f172a",
        )
        self.clock.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="nsew")

        self.status_badge = ctk.CTkLabel(
            self.read_panel,
            textvariable=self._status_var,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=999,
            fg_color="#dbeafe",
            text_color="#1d4ed8",
            padx=16,
            pady=8,
        )
        self.status_badge.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        self.controls = ctk.CTkFrame(self, corner_radius=18)
        self.controls.grid(row=0, column=1, padx=(4, 8), pady=8, sticky="nsew")
        self.controls.grid_columnconfigure(0, weight=1)
        self.controls.grid_columnconfigure(1, weight=1)
        self.controls.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            self.controls,
            text="Controles de la cuenta regresiva",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=(12, 10), sticky="w")

        ctk.CTkLabel(
            self.controls,
            text="Entradas de tiempo",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 6), sticky="w")

        selectors = ctk.CTkFrame(self.controls, fg_color="transparent")
        selectors.grid(
            row=2, column=0, columnspan=3, padx=12, pady=(0, 10), sticky="ew"
        )
        selectors.grid_columnconfigure(0, weight=1)
        selectors.grid_columnconfigure(1, weight=1)
        selectors.grid_columnconfigure(2, weight=1)

        self._hours_entry = self._build_entry_cell(
            selectors,
            column=0,
            label="Horas",
            variable=self._hours_var,
        )
        self._minutes_entry = self._build_entry_cell(
            selectors,
            column=1,
            label="Minutos",
            variable=self._minutes_var,
        )
        self._seconds_entry = self._build_entry_cell(
            selectors,
            column=2,
            label="Segundos",
            variable=self._seconds_var,
        )

        buttons = ctk.CTkFrame(self.controls, fg_color="transparent")
        buttons.grid(row=3, column=0, columnspan=3, padx=12, pady=(2, 0), sticky="ew")
        for index in range(4):
            buttons.grid_columnconfigure(index, weight=1)

        self.start_button = ctk.CTkButton(buttons, text="Iniciar", command=self.start)
        self.start_button.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="ew")

        self.pause_button = ctk.CTkButton(buttons, text="Pausar", command=self.pause)
        self.pause_button.grid(row=0, column=1, padx=6, pady=0, sticky="ew")

        self.resume_button = ctk.CTkButton(
            buttons, text="Reanudar", command=self.resume
        )
        self.resume_button.grid(row=0, column=2, padx=6, pady=0, sticky="ew")

        self.reset_button = ctk.CTkButton(
            buttons, text="Restablecer", command=self.reset
        )
        self.reset_button.grid(row=0, column=3, padx=(6, 0), pady=0, sticky="ew")

        ctk.CTkLabel(
            self.controls,
            text="Agregar/Reducir",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=4, column=0, columnspan=3, padx=12, pady=(10, 6), sticky="w")

        delta_inputs = ctk.CTkFrame(self.controls, fg_color="transparent")
        delta_inputs.grid(
            row=5, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew"
        )
        delta_inputs.grid_columnconfigure(0, weight=1)
        delta_inputs.grid_columnconfigure(1, weight=1)
        delta_inputs.grid_columnconfigure(2, weight=1)

        self._delta_hours_entry = self._build_entry_cell(
            delta_inputs,
            column=0,
            label="Horas",
            variable=self._delta_hours_var,
        )
        self._delta_minutes_entry = self._build_entry_cell(
            delta_inputs,
            column=1,
            label="Minutos",
            variable=self._delta_minutes_var,
        )
        self._delta_seconds_entry = self._build_entry_cell(
            delta_inputs,
            column=2,
            label="Segundos",
            variable=self._delta_seconds_var,
        )

        delta_buttons = ctk.CTkFrame(self.controls, fg_color="transparent")
        delta_buttons.grid(
            row=6, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew"
        )
        delta_buttons.grid_columnconfigure(0, weight=1)
        delta_buttons.grid_columnconfigure(1, weight=1)

        self.add_delta_button = ctk.CTkButton(
            delta_buttons,
            text="Agregar delta",
            command=lambda: self._apply_delta(1),
        )
        self.add_delta_button.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="ew")

        self.reduce_delta_button = ctk.CTkButton(
            delta_buttons,
            text="Reducir delta",
            command=lambda: self._apply_delta(-1),
        )
        self.reduce_delta_button.grid(row=0, column=1, padx=(6, 0), pady=0, sticky="ew")

        for entry in (self._hours_entry, self._minutes_entry, self._seconds_entry):
            entry.bind("<FocusOut>", self._on_input_focus_out)
            entry.bind("<Return>", self._on_input_commit)

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

    def _apply_delta(self, direction: int) -> None:
        hours = ValidationUtils.safe_int(self._delta_hours_var.get())
        minutes = ValidationUtils.safe_int(self._delta_minutes_var.get())
        seconds = ValidationUtils.safe_int(self._delta_seconds_var.get())

        delta_seconds = direction * TimeUtils.to_seconds(hours, minutes, seconds)
        self.adjust_time(delta_seconds)

        self._delta_hours_var.set("00")
        self._delta_minutes_var.set("00")
        self._delta_seconds_var.set("00")

    def _refresh_view(self, animate_clock: bool = False) -> None:
        state_text = {
            "ready": "Listo",
            "running": "En ejecución",
            "paused": "Pausado",
            "finished": "Finalizado",
        }[self._state]
        self._status_var.set(state_text)

        status_styles = {
            "ready": ("#dbeafe", "#1d4ed8"),
            "running": ("#dcfce7", "#166534"),
            "paused": ("#fef3c7", "#92400e"),
            "finished": ("#fee2e2", "#b91c1c"),
        }
        status_bg, status_text = status_styles[self._state]
        self.status_badge.configure(fg_color=status_bg, text_color=status_text)

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
        self._delta_hours_entry.configure(state="normal", text_color="#000000")
        self._delta_minutes_entry.configure(state="normal", text_color="#000000")
        self._delta_seconds_entry.configure(state="normal", text_color="#000000")
        self.add_delta_button.configure(state="normal")
        self.reduce_delta_button.configure(state="normal")

        hours, minutes, seconds = TimeUtils.from_seconds(self._remaining_seconds)

        digital = f"{hours:02}:{minutes:02}:{seconds:02}"
        display_hour = hours % 12 or 12
        display_time = datetime(2000, 1, 1, display_hour, minutes, seconds)
        if animate_clock:
            self.clock.animate_to_display(display_time, digital_text=digital)
        else:
            self.clock.set_display(display_time, digital_text=digital)
