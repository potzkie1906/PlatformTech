"""class InputPanel - the rounded input panel on the left of each tab
(plus input_textbox, the multi-line input box placed inside it).
"""

import customtkinter as ctk

from helpers import _focus_next
from theme import C, FONT, plain_button_style, px


def input_textbox(master):
    """Multi-line input box (request queue / reference string)."""
    box = ctk.CTkTextbox(master, width=InputPanel.WIDTH, height=64, wrap="word", undo=True,
                         corner_radius=8, border_width=2, fg_color=C("field"),
                         border_color=C("border_strong"), text_color=C("text"), font=FONT.ui)
    box.bind("<Tab>", _focus_next)
    return box


class InputPanel(ctk.CTkFrame):
    """The rounded panel on the left of each tab, laid out on a 2-column grid."""

    WIDTH = 300                              # width of the full-width input widgets

    def __init__(self, master, title):
        super().__init__(master, corner_radius=14, fg_color=C("card"))
        self.columnconfigure(0, weight=1, uniform="half")
        self.columnconfigure(1, weight=1, uniform="half")
        ctk.CTkLabel(self, text=title, font=FONT.title, text_color=C("text"), anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(14, 0))
        self.row = 1

    @staticmethod
    def _padx(column, span):
        return (18 if column == 0 else 5, 18 if column + span >= 2 else 5)

    def label(self, text, column=0, span=2, top=8, hint=None):
        ctk.CTkLabel(self, text=text, font=FONT.bold, text_color=C("text"), anchor="w",
                     height=20).grid(row=self.row, column=column, columnspan=span, sticky="w",
                                     padx=self._padx(column, span), pady=(top, 4))
        if hint:                                    # small grey note on the right
            ctk.CTkLabel(self, text=hint, font=FONT.small, text_color=C("muted"),
                         height=20).grid(row=self.row, column=1, sticky="e",
                                         padx=self._padx(1, 1), pady=(top, 4))

    def put(self, widget, column=0, span=2, top=0, sticky="ew"):
        widget.grid(row=self.row, column=column, columnspan=span, sticky=sticky,
                    padx=self._padx(column, span), pady=(top, 0))
        return widget

    def next_row(self):
        self.row += 1

    def description(self):
        """Blue box that explains the selected algorithm."""
        return ctk.CTkLabel(self, text="", font=FONT.small, text_color=C("text"),
                            fg_color=C("accent_soft"), corner_radius=8, justify="left",
                            anchor="w", wraplength=self.WIDTH - 24, padx=px(10), pady=px(8))

    def buttons(self, solve, compare, example, clear):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(row=self.row, column=0, columnspan=2, sticky="ew", padx=18, pady=(16, 16))
        box.columnconfigure(0, weight=1, uniform="buttons")
        box.columnconfigure(1, weight=1, uniform="buttons")
        ctk.CTkButton(box, text="Solve", command=solve, height=36, corner_radius=8,
                      font=FONT.bold, fg_color=C("accent"), hover_color=C("accent_hover")).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(box, text="Compare all", command=compare, height=36, corner_radius=8,
                      font=FONT.bold, fg_color="transparent", border_width=2,
                      border_color=C("accent"), text_color=C("accent_text"),
                      hover_color=C("accent_soft")).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ctk.CTkButton(box, text="Load example", command=example, **plain_button_style()).grid(
            row=1, column=0, sticky="ew", padx=(0, 4), pady=(8, 0))
        ctk.CTkButton(box, text="Clear", command=clear, **plain_button_style()).grid(
            row=1, column=1, sticky="ew", padx=(4, 0), pady=(8, 0))
        self.row += 1
