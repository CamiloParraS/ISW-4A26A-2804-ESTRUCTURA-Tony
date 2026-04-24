import tkinter as tk


def run_ui():
    root = tk.Tk()
    root.title("Tkinter Window")
    root.geometry("320x160")
    label = tk.Label(root, text="Hello from tkinter")
    label.pack(expand=True)
    root.mainloop()
