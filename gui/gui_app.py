# gui/gui_app.py

import tkinter as tk
from tkinter import messagebox
from logic.your_logic import process_data  # Import your logic functions

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("My Application")

        # Create and layout your widgets
        self.label = tk.Label(root, text="Enter a number:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(pady=10)

        self.button = tk.Button(root, text="Process", command=self.on_button_click)
        self.button.pack(pady=10)

    def on_button_click(self):
        try:
            value = int(self.entry.get())
            result = process_data(value)
            messagebox.showinfo("Result", f"Processed Value: {result}")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid integer.")

def run_app():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
