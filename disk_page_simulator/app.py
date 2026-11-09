"""class App - the main window: header, page switcher and dark-mode switch."""

import tkinter as tk

import customtkinter as ctk

from bankers_tab import BankersTab
from disk_tab import DiskTab
from lab_widgets import configure_ttk
from page_tab import PageTab
from priority_tab import PriorityTab
from round_robin_tab import RoundRobinTab
from theme import C, FONT, segment_style, setup_fonts


class App(ctk.CTk):
    PAGE_TYPES = {
        "Priority": PriorityTab,
        "Round Robin": RoundRobinTab,
        "Page Replacement": PageTab,
        "Disk Scheduling": DiskTab,
        "Banker's": BankersTab,
    }
    TABS = tuple(PAGE_TYPES)

    def __init__(self):
        super().__init__(fg_color=C("bg"))
        setup_fonts(self)
        configure_ttk(self)
        self.title("Operating Systems Simulator")
        self.geometry("1280x800")
        self.minsize(1040, 660)
        self.compare_windows = []

        # header: title, page switcher and dark-mode switch
        header = ctk.CTkFrame(self, corner_radius=0, fg_color=C("card"))
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Operating Systems Simulator",
                     font=FONT.header, text_color=C("text")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(8, 3))
        self.dark_var = tk.BooleanVar(master=self, value=ctk.get_appearance_mode() == "Dark")
        ctk.CTkSwitch(header, text="Dark mode", variable=self.dark_var, onvalue=True,
                      offvalue=False, command=self._toggle_dark, font=FONT.ui,
                      text_color=C("text"), progress_color=C("accent")).grid(
            row=0, column=1, sticky="e", padx=20, pady=(8, 3))
        self.tabs = ctk.CTkSegmentedButton(header, values=list(self.TABS),
                                           command=self._show_page, **segment_style())
        self.tabs.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 8))
        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=C("border")).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.pages = {name: page_type(body) for name, page_type in self.PAGE_TYPES.items()}
        self.tabs.set(self.TABS[0])
        self._show_page(self.TABS[0])
        self.after(50, self._maximize)

    def _maximize(self):
        try:
            self.state("zoomed")                     # Windows / macOS
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)     # Linux
            except tk.TclError:
                pass

    def _show_page(self, name):
        for key, page in self.pages.items():
            if key == name:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()

    def _toggle_dark(self):
        ctk.set_appearance_mode("dark" if self.dark_var.get() else "light")
        configure_ttk(self)
        for page in self.pages.values():
            page.refresh_theme()
        for window in list(self.compare_windows):
            window.draw()