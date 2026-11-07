"""class StatCard - a box that shows one result, e.g. 'Total head movement 236'."""

import customtkinter as ctk

from theme import C, FONT


class StatCard(ctk.CTkFrame):
    """A box that shows one result, e.g. 'Total head movement  236'."""

    def __init__(self, master, caption, color="text"):
        super().__init__(master, corner_radius=12, fg_color=C("card"))
        ctk.CTkLabel(self, text=caption, font=FONT.small, text_color=C("muted"),
                     height=18).pack(anchor="w", padx=16, pady=(12, 0))
        self.value = ctk.CTkLabel(self, text="-", font=FONT.big, text_color=C(color), height=38)
        self.value.pack(anchor="w", padx=16)
        self.note = ctk.CTkLabel(self, text=" ", font=FONT.small, text_color=C("muted"),
                                 height=18)
        self.note.pack(anchor="w", padx=16, pady=(0, 12))

    def show(self, value, note=" "):
        self.value.configure(text=value)
        self.note.configure(text=note)
