"""Start Topic 2 with the Round Robin time-quantum setting."""

import tkinter as tk
from tkinter import ttk

from cpu_core import MAX_TIME, whole
from cpu_view import CPUView
from round_robin import round_robin


class RoundRobinTab(CPUView):
    with_priority = False
    example_rows = "P1   0   7\nP2   2   4\nP3   4   1\nP4   5   4"

    def build_options(self, parent):
        self.quantum = tk.StringVar(master=self, value="2")
        ttk.Label(parent, text="RR time quantum").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.quantum, width=10).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(parent, text="Arrivals at a slice boundary enter the ready queue before the running process requeues.",
                  style="Muted.TLabel", wraplength=252).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    def restore_settings(self):
        self.quantum.set("2")

    def extra_schedule(self, jobs):
        return round_robin(jobs, whole(self.quantum.get(), "RR time quantum", 1, MAX_TIME))