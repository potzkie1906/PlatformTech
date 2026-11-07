"""Disk Scheduling & Page Replacement Simulator  (CustomTkinter version)
=====================================================================
A desktop app that solves two classic Operating Systems problems and shows
HOW each answer is found, step by step.

DISK SCHEDULING  -  FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK
PAGE REPLACEMENT  -  FIFO, LRU, OPTIMAL

Install once:   pip install customtkinter
How to run (inside this folder):
    python main.py           -> opens the app
    python main.py --test    -> checks the algorithms against textbook answers

Files (one class per file):
    main.py             starts the program                (this file)
    app.py              class App            - main window
    disk_tab.py         class DiskTab        - Disk Scheduling page
    page_tab.py         class PageTab        - Page Replacement page
    compare_window.py   class CompareWindow  - "Compare all" pop-up
    input_panel.py      class InputPanel     - input panel on the left
    canvas_card.py      class CanvasCard     - card with a drawing canvas
    stat_card.py        class StatCard       - result box
    stepper.py          class Stepper        - number box with - and +
    legend.py           class Legend         - colour legend
    theme.py            colours, fonts and widget styles
    helpers.py          small helper functions
    disk_algorithms.py  PART 1 - disk scheduling algorithms
    page_algorithms.py  PART 2 - page replacement algorithms
    self_test.py        the --test check
"""

import sys

try:
    import customtkinter as ctk
except ImportError:            # friendly message instead of a long error
    sys.exit("This program uses CustomTkinter, which is not installed yet.\n"
             "Install it with:   pip install customtkinter")

from app import App
from self_test import run_self_test


def main():
    if "--test" in sys.argv:
        sys.exit(0 if run_self_test() else 1)
    ctk.set_appearance_mode("light")        # the switch in the header changes it
    ctk.set_default_color_theme("blue")
    App().mainloop()


if __name__ == "__main__":
    main()
