"""class Stepper - a number box with - and + buttons (CustomTkinter has no spinbox)."""

import customtkinter as ctk

from helpers import set_entry
from theme import FONT, entry_style, plain_button_style


class Stepper(ctk.CTkFrame):
    """A number box with - and + buttons (CustomTkinter has no spinbox)."""

    def __init__(self, master, low, high, command=None):
        super().__init__(master, fg_color="transparent")
        self.low, self.high, self.command = low, high, command
        style = plain_button_style()
        style.update(width=36, font=FONT.bold)
        ctk.CTkButton(self, text="−", command=lambda: self.step(-1), **style).grid(
            row=0, column=0)
        self.entry = ctk.CTkEntry(self, width=64, justify="center", **entry_style())
        self.entry.grid(row=0, column=1, padx=6)
        ctk.CTkButton(self, text="+", command=lambda: self.step(1), **style).grid(row=0, column=2)

    def get(self):
        return self.entry.get()

    def set(self, value):
        set_entry(self.entry, str(value))

    def step(self, delta):
        try:
            value = int(self.entry.get()) + delta
        except ValueError:
            value = self.low
        self.set(min(self.high, max(self.low, value)))
        if self.command is not None:
            self.command()
