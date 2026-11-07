"""class Legend - the small colour legend shown on top of a graph or table."""

import tkinter as tk

from theme import CFONT, P, px


class Legend(tk.Canvas):
    """A small legend strip, redrawn in the colours of the current theme."""

    def __init__(self, master, entries):
        super().__init__(master, highlightthickness=0, bd=0, height=px(20))
        self.entries = entries               # [(symbol, colour name, label), ...]
        self.draw()

    def draw(self):
        pal = P()
        self.delete("all")
        self.configure(bg=pal["card"])
        x, y, r = px(2), px(10), px(5)
        for symbol, colour, label in self.entries:
            color = pal[colour]
            if symbol == "dot":
                self.create_oval(x, y - r, x + 2 * r, y + r, fill=color, outline="")
                x += 2 * r
            elif symbol == "ring":
                self.create_oval(x + 1, y - r + 1, x + 2 * r - 1, y + r - 1,
                                 fill=pal["card"], outline=color, width=2)
                x += 2 * r
            elif symbol == "dash":
                self.create_line(x, y, x + px(22), y, fill=color, width=2, dash=(5, 3))
                x += px(22)
            elif symbol == "box":
                self.create_rectangle(x, y - r - 1, x + 2 * r + 4, y + r + 1,
                                      fill=color, outline=pal["border"])
                x += 2 * r + 4
            x += px(5)
            self.create_text(x, y, text=label, anchor="w", font=CFONT.small, fill=pal["muted"])
            x += CFONT.small.measure(label) + px(14)
        self.configure(width=x)
