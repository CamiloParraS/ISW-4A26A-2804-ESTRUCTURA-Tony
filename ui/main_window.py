from __future__ import annotations

import customtkinter as ctk

from ui.tabs import build_clock_tab, build_countdown_tab

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TONY El Reloj")
        self.geometry("880x580")
        self.minsize(760, 540)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(
            self,
            segmented_button_selected_hover_color="#1d4ed8",
        )
        self.tabview.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        self.tabview.add("Clock")
        self.tabview.add("Countdown")

        self.clock_tab = build_clock_tab(self.tabview.tab("Clock"))
        self.clock_tab.pack(fill="both", expand=True)

        self.countdown_tab = build_countdown_tab(self.tabview.tab("Countdown"))
        self.countdown_tab.pack(fill="both", expand=True)

        self.bind_all("<Left>", self._on_left_shortcut, add="+")
        self.bind_all("<Right>", self._on_right_shortcut, add="+")
        self.bind_all("<space>", self._on_space_shortcut, add="+")

    def _clock_tab_is_active(self) -> bool:
        return self.tabview.get() == "Clock"

    def _on_left_shortcut(self, _event: object) -> str | None:
        if not self._clock_tab_is_active():
            return None
        if hasattr(self.clock_tab, "on_shortcut_left"):
            self.clock_tab.on_shortcut_left()
        return "break"

    def _on_right_shortcut(self, _event: object) -> str | None:
        if not self._clock_tab_is_active():
            return None
        if hasattr(self.clock_tab, "on_shortcut_right"):
            self.clock_tab.on_shortcut_right()
        return "break"

    def _on_space_shortcut(self, _event: object) -> str | None:
        if not self._clock_tab_is_active():
            return None
        if hasattr(self.clock_tab, "on_shortcut_local"):
            self.clock_tab.on_shortcut_local()
        return "break"


def run_ui():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_ui()
