"""Small helper functions used by the windows: number formatting, input checking,
text boxes, mouse-wheel scrolling and drawing tables on a canvas.
"""

import math
import re
from decimal import Decimal, ROUND_HALF_UP

import customtkinter as ctk

from theme import C, CFONT, FONT, P, px


def fmt(number):
    """Show a number without useless decimals: 640.0 -> '640', 0.50 -> '0.5'."""
    return f"{number:.4f}".rstrip("0").rstrip(".")


def two_dp(number):
    """Round to 2 decimal places the way it is done by hand: 19.125 -> '19.13'."""
    return str(Decimal(repr(number)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _sign(value):
    return (value > 0) - (value < 0)


def split_tokens(text):
    """'98, 183 37;122' -> ['98', '183', '37', '122']"""
    return [t for t in re.split(r"[\s,;]+", text.strip()) if t]


def read_int(text, what, low, high=None):
    """Turn the text of an input box into an int, with a friendly error."""
    text = text.strip()
    if not text:
        raise ValueError(f"Please enter the {what}.")
    try:
        value = int(text)
    except ValueError:
        raise ValueError(f"The {what} must be a whole number (you typed '{text}').") from None
    if value < low or (high is not None and value > high):
        limit = f"between {low} and {high}" if high is not None else f"at least {low}"
        raise ValueError(f"The {what} must be {limit}.")
    return value


def _focus_next(event):
    """Make Tab move to the next field instead of typing a tab character."""
    event.widget.tk_focusNext().focus_set()
    return "break"


def output_textbox(master, wrap):
    """Read-only text area for the written solution / explanation."""
    return ctk.CTkTextbox(master, wrap=wrap, state="disabled", corner_radius=0, border_width=0,
                          fg_color=C("card"), text_color=C("text"), font=FONT.mono,
                          scrollbar_button_color=C("scroll"),
                          scrollbar_button_hover_color=C("scroll_hover"))


def set_entry(entry, text):
    entry.delete(0, "end")
    if text:
        entry.insert(0, text)


def set_text(box, text):
    box.delete("1.0", "end")
    box.insert("1.0", text)


def write_text(box, parts):
    """Replace everything in a read-only text area.
    parts = [("some text", "tag name or None"), ...]"""
    pal = P()
    for tag, colour in (("h", "accent_text"), ("b", "accent_text"), ("muted", "muted"),
                        ("answer", "good"), ("fault", "fault_fg"), ("hit", "hit_fg")):
        box.tag_config(tag, foreground=pal[colour])      # CTkTextbox tags can't change font
    box.configure(state="normal")
    box.delete("1.0", "end")
    for chunk, tag in parts:
        if tag:
            box.insert("end", chunk, tag)
        else:
            box.insert("end", chunk)
    box.configure(state="disabled")


def bind_mousewheel(canvas, sideways_first=False):
    """Scroll a canvas with the mouse wheel while the pointer is over it.
    Hold Shift to scroll in the other direction."""
    def on_wheel(event):
        if event.num == 4 or getattr(event, "delta", 0) > 0:
            step = -1
        elif event.num == 5 or getattr(event, "delta", 0) < 0:
            step = 1
        else:
            return
        shift = isinstance(event.state, int) and bool(event.state & 0x0001)
        if sideways_first != shift:
            canvas.xview_scroll(step, "units")
        else:
            canvas.yview_scroll(step, "units")

    def on_enter(_event):
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            canvas.bind_all(sequence, on_wheel)

    def on_leave(_event):
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            canvas.unbind_all(sequence)

    canvas.bind("<Enter>", on_enter, add="+")
    canvas.bind("<Leave>", on_leave, add="+")


def _pull_back(x1, y1, x2, y2, amount):
    """Shorten a line so that its arrow head stops at the edge of the dot."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length <= amount:
        return x2, y2
    return x2 - dx / length * amount, y2 - dy / length * amount


def draw_table(canvas, headers, rows, style=None, align=None, fill_width=0, min_width=0,
               stretch="last"):
    """Draw a table on a canvas and return its full (width, height).
    style(row, column) may return {"bg": ..., "fg": ..., "font": ...} for one cell.
    If fill_width is wider than the table, the extra space goes to the last
    column (stretch="last") or is shared by every column (stretch="all")."""
    pal = P()
    pad = px(12)
    cell_h = CFONT.ui.metrics("linespace") + px(14)
    align = align or ["center"] * len(headers)
    widths = []
    for col, title in enumerate(headers):
        longest = max([CFONT.bold.measure(title)]
                      + [CFONT.bold.measure(str(row[col])) for row in rows])
        widths.append(max(min_width, longest + 2 * pad))
    extra = fill_width - sum(widths)
    if extra > 0 and stretch == "all":
        widths = [w + extra / len(widths) for w in widths]
    elif extra > 0:
        widths[-1] += extra

    def cell(x, y, w, text, bg, fg, font, where):
        canvas.create_rectangle(x, y, x + w, y + cell_h, fill=bg, outline=pal["border"])
        if where == "w":
            canvas.create_text(x + pad, y + cell_h / 2, text=text, fill=fg, font=font, anchor="w")
        else:
            canvas.create_text(x + w / 2, y + cell_h / 2, text=text, fill=fg, font=font)

    x = start = 1
    for col, title in enumerate(headers):                    # header row
        cell(x, start, widths[col], title, pal["soft"], pal["text"], CFONT.bold, align[col])
        x += widths[col]
    for r, row in enumerate(rows):                           # body rows
        x, y = start, start + (r + 1) * cell_h
        for col, text in enumerate(row):
            look = {"bg": pal["card"], "fg": pal["text"], "font": CFONT.ui}
            if style is not None:
                look.update(style(r, col) or {})
            cell(x, y, widths[col], str(text), look["bg"], look["fg"], look["font"], align[col])
            x += widths[col]
    return start + sum(widths) + 1, start + (len(rows) + 1) * cell_h + 1
