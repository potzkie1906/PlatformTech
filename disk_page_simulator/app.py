"""class App - the main window: header, page switcher and dark-mode switch."""

import tkinter as tk

import customtkinter as ctk

from disk_tab import DiskTab
from page_tab import PageTab
from theme import C, FONT, segment_style, setup_fonts


class App(ctk.CTk):
    TABS = ("Disk Scheduling", "Page Replacement")

    def __init__(self):
        super().__init__(fg_color=C("bg"))
        setup_fonts(self)
        self.title("Disk Scheduling & Page Replacement Simulator")
        self.geometry("1280x800")
        self.minsize(1040, 660)
        self.compare_windows = []

        # header: title, page switcher and dark-mode switch
        header = ctk.CTkFrame(self, corner_radius=0, fg_color=C("card"))
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Disk Scheduling & Page Replacement Simulator",
                     font=FONT.header, text_color=C("text")).pack(side="left", padx=20, pady=12)
        self.dark_var = tk.BooleanVar(value=ctk.get_appearance_mode() == "Dark")
        ctk.CTkSwitch(header, text="Dark mode", variable=self.dark_var, onvalue=True,
                      offvalue=False, command=self._toggle_dark, font=FONT.ui,
                      text_color=C("text"), progress_color=C("accent")).pack(
            side="right", padx=(16, 20))
        self.tabs = ctk.CTkSegmentedButton(header, values=list(self.TABS),
                                           command=self._show_page, **segment_style())
        self.tabs.pack(side="right", pady=12)
        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=C("border")).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.pages = {self.TABS[0]: DiskTab(body), self.TABS[1]: PageTab(body)}
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
        for page in self.pages.values():
            page.refresh_theme()
        for window in list(self.compare_windows):
            window.draw()
