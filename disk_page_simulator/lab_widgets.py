"""Embedded ttk panels and their shared styles."""

import tkinter as tk
from tkinter import font, ttk

from theme import CFONT, FONT, P, px


def configure_ttk(root):
    p = P()
    style = ttk.Style(root)
    style.theme_use("clam")
    family = font.nametofont("TkDefaultFont", root=root).actual("family")
    style.configure(".", font=(family, 10), foreground=p["text"], background=p["card"])
    style.configure("TFrame", background=p["card"])
    style.configure("Body.TFrame", background=p["bg"])
    style.configure("TLabel", foreground=p["text"], background=p["card"])
    style.configure("Muted.TLabel", foreground=p["muted"])
    style.configure("Heading.TLabel", font=(family, 13, "bold"))
    style.configure("Accent.TLabel", foreground=p["accent_text"], font=(family, 11, "bold"))
    style.configure("Alert.TLabel", foreground=p["fault_fg"], font=(family, 11, "bold"))
    style.configure("Status.TLabel", foreground=p["muted"], background=p["bg"])
    style.configure("Error.Status.TLabel", foreground=p["fault_fg"], background=p["bg"])
    style.configure("TButton", padding=(10, 6), bordercolor=p["border"])
    style.map("TButton", background=[("active", p["soft"])])
    style.configure("Primary.TButton", background=p["accent_deep"], foreground="white")
    style.map("Primary.TButton", background=[("active", p["accent_hover"])])
    for name in ("TEntry", "TSpinbox", "TCombobox"):
        style.configure(name, padding=(5, 4), fieldbackground=p["field"],
                        foreground=p["text"], bordercolor=p["border"], insertcolor=p["text"])
    style.map("TCombobox", fieldbackground=[("readonly", p["field"])],
              foreground=[("readonly", p["text"])])
    style.configure("Treeview", background=p["card"], fieldbackground=p["card"],
                    foreground=p["text"], rowheight=27)
    style.configure("Treeview.Heading", background=p["soft"], foreground=p["text"],
                    font=(family, 10, "bold"), padding=(3, 5))
    style.map("Treeview", background=[("selected", p["accent_soft"])],
              foreground=[("selected", p["text"])])
    style.configure("TNotebook", background=p["bg"], bordercolor=p["border"])
    style.configure("TNotebook.Tab", padding=(10, 5), background=p["soft"],
                    bordercolor=p["border"], foreground=p["text"])
    style.map("TNotebook.Tab", background=[("selected", p["card"]), ("active", p["accent_soft"])])
    style.configure("TScrollbar", background=p["scroll"], troughcolor=p["field"],
                    lightcolor=p["scroll"], darkcolor=p["scroll"], arrowcolor=p["text"],
                    bordercolor=p["border"])
    root.option_add("*TCombobox*Listbox.background", p["field"])
    root.option_add("*TCombobox*Listbox.foreground", p["text"])
    family = FONT.ui.cget("family")
    ui_size = -px(FONT.ui.cget("size"))
    bold = (family, -px(FONT.bold.cget("size")), "bold")
    title = (family, -px(FONT.title.cget("size")), "bold")

    body = font.nametofont("TkDefaultFont", root=root)
    body.configure(family=family, size=ui_size)
    font.nametofont("TkTextFont", root=root).configure(family=family, size=ui_size)
    font.nametofont("TkFixedFont", root=root).configure(size=ui_size)

    style.configure(".", font=body)
    style.configure("Heading.TLabel", font=title)
    style.configure("Accent.TLabel", font=bold)
    style.configure("Alert.TLabel", font=bold)
    style.configure(
        "Treeview",
        font=CFONT.ui,
        rowheight=CFONT.ui.metrics("linespace") + px(14),
    )
    style.configure("Treeview.Heading", font=CFONT.bold)


class LabPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Body.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.body = ttk.Frame(self, style="Body.TFrame", padding=(14, 12, 14, 0))
        self.body.grid(row=0, column=0, sticky="nsew")
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)

        self.status = ttk.Label(self, padding=(17, 6), style="Status.TLabel", anchor="w")
        self.status.grid(row=1, column=0, sticky="ew")
        wrap_to_width(self.status)

    def feedback(self, text, *, error=False):
        style = "Error.Status.TLabel" if error else "Status.TLabel"
        self.status.configure(text=text, style=style)

    def refresh_theme(self):
        p = P()
        pending = self.winfo_children()
        while pending:
            widget = pending.pop()
            pending.extend(widget.winfo_children())
            if isinstance(widget, tk.Text):
                widget.configure(bg=p["field"], fg=p["text"], insertbackground=p["text"],
                                 highlightbackground=p["border"], highlightcolor=p["accent"])
            elif isinstance(widget, ttk.Treeview):
                widget.tag_configure("alternate", background=p["soft"])


def wrap_to_width(label: ttk.Label):
    label.bind("<Configure>", lambda event: label.configure(wraplength=max(40, event.width - 4)))


def input_text(parent, *, width: int, height: int) -> tuple[ttk.Frame, tk.Text]:
    frame = ttk.Frame(parent)
    p = P()
    text = tk.Text(frame, width=width, height=height, wrap="none", undo=True,
                   font="TkFixedFont", bg=p["field"], fg=p["text"], insertbackground=p["text"],
                   highlightcolor=p["accent"], highlightbackground=p["border"],
                   highlightthickness=1, relief="flat", padx=7, pady=5)
    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
    x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    text.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    return frame, text


def set_text(widget: tk.Text, text: str):
    widget.delete("1.0", "end")
    widget.insert("1.0", text)
    widget.edit_reset()


def table(parent, headings, widths, *, height=6) -> ttk.Treeview:
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    tree = ttk.Treeview(frame, columns=headings, show="headings", height=height)
    for name, width in zip(headings, widths, strict=True):
        tree.heading(name, text=name)
        tree.column(name, width=width, minwidth=width, stretch=False, anchor="center")
    tree.tag_configure("alternate", background=P()["soft"])
    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    tree.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    return tree


def fill_table(tree: ttk.Treeview, rows):
    tree.delete(*tree.get_children())
    for index, row in enumerate(rows):
        tree.insert("", "end", values=row, tags=("alternate",) if index % 2 else ())
    tree.yview_moveto(0)
    tree.xview_moveto(0)