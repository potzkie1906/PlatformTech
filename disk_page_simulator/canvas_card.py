"""class CanvasCard - a rounded card with a title, an optional legend and a
scrollable drawing canvas (used for the graph and the tables).
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from helpers import bind_mousewheel
from legend import Legend
from theme import C, CFONT, FONT, P, px


class CanvasCard(ctk.CTkFrame):
    """A rounded card with a title, an optional legend and a scrollable canvas."""

    def __init__(self, master, title, legend=None, sideways_wheel=False):
        super().__init__(master, corner_radius=12, fg_color=C("card"))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 6))
        ctk.CTkLabel(top, text=title, font=FONT.bold, text_color=C("text"),
                     height=22).pack(side="left")
        self.legend = Legend(top, legend) if legend else None
        if self.legend is not None:
            self.legend.pack(side="right")

        # a plain tkinter Canvas (CustomTkinter has no drawing widget of its own)
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=P()["card"],
                                width=px(260), height=px(140))
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=(px(12), 0), pady=(0, px(10)))
        self.ybar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview,
                                     button_color=C("scroll"), button_hover_color=C("scroll_hover"))
        self.xbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview,
                                     button_color=C("scroll"), button_hover_color=C("scroll_hover"))
        self.ybar.grid(row=1, column=1, sticky="ns", padx=(2, 6), pady=(0, 10))
        self.xbar.grid(row=2, column=0, sticky="ew", padx=(12, 0), pady=(0, 10))
        self.canvas.configure(xscrollcommand=self.xbar.set, yscrollcommand=self.ybar.set)
        self.content_size = (0, 0)
        self.on_resize: Optional[Callable[[], None]] = None   # function that redraws this card
        self._job = None
        self.canvas.bind("<Configure>", self._resized)
        bind_mousewheel(self.canvas, sideways_first=sideways_wheel)

    def _resized(self, _event=None):
        if self._job is not None:
            self.after_cancel(self._job)
        self._job = self.after(40, self._redraw)

    def _redraw(self):
        self._job = None
        if self.on_resize is not None:
            self.on_resize()

    def start(self):
        """Clear the canvas before drawing. Returns (canvas, width, height)."""
        c = self.canvas
        c.delete("all")
        c.configure(bg=P()["card"])
        return c, max(c.winfo_width(), px(200)), max(c.winfo_height(), px(80))

    def finish(self, width, height):
        """Tell the canvas how big the drawing is; show scroll bars only if needed."""
        c = self.canvas
        c.configure(scrollregion=(0, 0, width, height))
        self.content_size = (width, height)
        if width > c.winfo_width() + 1:
            self.xbar.grid()
        else:
            self.xbar.grid_remove()
        if height > c.winfo_height() + 1:
            self.ybar.grid()
        else:
            self.ybar.grid_remove()

    def message(self, text):
        """Show a grey message in the middle of the card."""
        c, width, height = self.start()
        c.create_text(width / 2, height / 2, text=text, fill=P()["muted"], font=CFONT.ui,
                      justify="center")
        self.finish(width, height)

    def refresh_theme(self):
        if self.legend is not None:
            self.legend.draw()
