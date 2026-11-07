"""class CompareWindow - the 'Compare all' pop-up window (bar chart + table)."""

import customtkinter as ctk

from canvas_card import CanvasCard
from helpers import draw_table
from theme import C, CFONT, FONT, P, plain_button_style, px


class CompareWindow(ctk.CTkToplevel):
    """Bar chart + table comparing every algorithm on the same input."""

    def __init__(self, master, title, subtitle, unit, bars, headers, rows, align,
                 stretch="last"):
        super().__init__(master, fg_color=C("bg"))
        self.app = master.winfo_toplevel()
        self.app.compare_windows.append(self)
        self.title(title)
        height = min(680, 250 + len(bars) * 32 + (len(rows) + 1) * 38)
        self.geometry(f"880x{height}")
        self.minsize(560, 380)
        self.transient(self.app)
        self.after(150, self._bring_to_front)

        self.bars, self.unit = bars, unit
        self.headers, self.rows, self.align, self.stretch = headers, rows, align, stretch
        self.best = min(value for _, value in bars)
        winners = [name for name, value in bars if value == self.best]
        self.winners = winners

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=16)
        ctk.CTkLabel(body, text=title, font=FONT.title, text_color=C("text"),
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(body, text=subtitle, font=FONT.small, text_color=C("muted"), anchor="w",
                     justify="left", wraplength=820).pack(anchor="w", pady=(2, 10))
        self.chart = CanvasCard(body, "Total per algorithm (lower is better)")
        self.chart.canvas.configure(height=len(bars) * px(32) + px(6))
        self.chart.pack(fill="x")
        self.chart.on_resize = self.draw
        ctk.CTkLabel(body, text=f"Lowest (best): {' and '.join(winners)} with "
                                f"{self.best} {unit}",
                     font=FONT.bold, text_color=C("good"), anchor="w").pack(anchor="w", pady=(8, 0))
        self.table = CanvasCard(body, "Details")
        self.table.pack(fill="both", expand=True, pady=(8, 0))
        self.table.on_resize = self.draw
        ctk.CTkButton(body, text="Close", width=110, command=self.destroy,
                      **plain_button_style()).pack(anchor="e", pady=(12, 0))
        self.bind("<Escape>", lambda e: self.destroy())
        self.draw()

    def _bring_to_front(self):
        self.lift()
        self.focus_set()

    def destroy(self):
        if self in self.app.compare_windows:
            self.app.compare_windows.remove(self)
        super().destroy()

    def draw(self):
        pal = P()
        c, width, _height = self.chart.start()
        label_w = max(CFONT.bold.measure(name) for name, _ in self.bars) + px(14)
        value_w = max(CFONT.ui.measure(f"{value} {self.unit}") for _, value in self.bars) + px(16)
        span = max(px(40), width - label_w - value_w)
        largest = max(value for _, value in self.bars) or 1
        bar_h, gap = px(24), px(8)
        for i, (name, value) in enumerate(self.bars):
            y = px(3) + i * (bar_h + gap)
            middle = y + bar_h / 2
            length = max(px(3), span * value / largest)
            color = pal["good"] if value == self.best else pal["accent"]
            c.create_text(label_w - px(10), middle, text=name, anchor="e", font=CFONT.bold,
                          fill=pal["text"])
            c.create_rectangle(label_w, y, label_w + length, y + bar_h, fill=color, outline="")
            c.create_text(label_w + length + px(8), middle, text=f"{value} {self.unit}",
                          anchor="w", font=CFONT.ui, fill=pal["text"])
        self.chart.finish(width, px(3) + len(self.bars) * (bar_h + gap))

        c, width, _height = self.table.start()

        def style(row, _col):
            if self.rows[row][0] in self.winners:
                return {"bg": pal["hit_bg"], "fg": pal["hit_fg"]}
            return None

        size = draw_table(c, self.headers, self.rows, style, align=self.align,
                          fill_width=width - px(2), stretch=self.stretch)
        self.table.finish(*size)
