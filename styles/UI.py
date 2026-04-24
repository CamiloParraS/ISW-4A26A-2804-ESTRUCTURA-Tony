import customtkinter


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("TONY")
        self.geometry("420x200")

        self.label = customtkinter.CTkLabel(
            self,
            text="Is time to use the clock!!!!",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.label.pack(expand=True)


def run_ui():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_ui()
