"""Start Topic 1. Use the priority convention assigned in class."""

import tkinter as tk
from tkinter import ttk

from cpu_core import INPUT_ORDER, PROCESS_ID
from cpu_view import CPUView
from priority import HIGH_FIRST, LOW_FIRST, NON_PREEMPTIVE, PREEMPTIVE, priority_schedule


class PriorityTab(CPUView):
    with_priority = True
    example_rows = "P1   0   7   4\nP2   2   4   1\nP3   4   1   3\nP4   5   4   2"

    def build_options(self, parent):
        self.mode = tk.StringVar(master=self, value=NON_PREEMPTIVE)
        self.order = tk.StringVar(master=self, value=LOW_FIRST)
        self.tie = tk.StringVar(master=self, value=INPUT_ORDER)
        options = (
            ("Priority mode", self.mode, (NON_PREEMPTIVE, PREEMPTIVE)),
            ("Higher priority", self.order, (LOW_FIRST, HIGH_FIRST)),
            ("Break same-arrival ties by", self.tie, (INPUT_ORDER, PROCESS_ID)),
        )
        for row, (label, variable, values) in enumerate(options):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Combobox(parent, textvariable=variable, values=values, width=18,
                         state="readonly").grid(row=row, column=1, sticky="ew", padx=(6, 0))

    def restore_settings(self):
        self.mode.set(NON_PREEMPTIVE)
        self.order.set(LOW_FIRST)
        self.tie.set(INPUT_ORDER)

    def tie_break(self):
        return self.tie.get()

    def extra_schedule(self, jobs):
        return priority_schedule(jobs, self.mode.get(), self.order.get(), self.tie_break())