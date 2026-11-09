"""Desktop interface for the Banker's Algorithm simulator."""

import re
import tkinter as tk
from tkinter import font, ttk

from bankers import (
    MAX_PROCESSES, MAX_RESOURCES, MAX_UNITS, BankState, check_request, check_safety,
)
from lab_widgets import LabPanel, fill_table, input_text, set_text, table, wrap_to_width

SAFE_EXAMPLE = (
    3, 2, "A B", "5 3",
    "2 0\n1 1\n1 1", "5 2\n2 2\n3 2",
    "P1", "1 1",
)
UNSAFE_EXAMPLE = (2, 1, "A", "3", "2\n1", "3\n2", "", "")


def vector_text(values):
    return "[" + ", ".join(map(str, values)) + "]"


def flags_text(flags):
    return vector_text("T" if finished else "F" for finished in flags)


def comparison_text(blocking, names):
    return "YES" if not blocking else "NO · " + ", ".join(names[index] for index in blocking)


def cells(text):
    return [cell.strip() for cell in text.split(",")] if "," in text else text.split()


def read_integer(text, label, minimum, maximum):
    try:
        number = int(text)
    except ValueError:
        raise ValueError(f"{label} must be a whole number.") from None
    if not minimum <= number <= maximum:
        raise ValueError(f"{label} must be between {minimum:,} and {maximum:,}.")
    return number


def read_vector(text, label, width):
    values = cells(text)
    if len(values) != width:
        raise ValueError(f"{label} needs {width} resource values. Found {len(values)}.")
    return tuple(read_integer(value, f"{label}, column {index}", 0, MAX_UNITS)
                 for index, value in enumerate(values, 1))


def read_matrix(text, label, count, width):
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) != count:
        raise ValueError(f"{label} needs {count} process rows. Found {len(lines)}.")
    return tuple(read_vector(line, f"{label} P{index}", width) for index, line in enumerate(lines))


class StateView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=9)
        self.heading = ttk.Label(self, style="Heading.TLabel")
        self.heading.pack(fill="x", pady=(0, 4))
        self.legend = ttk.Label(self, style="Muted.TLabel", wraplength=500)
        self.legend.pack(fill="x", pady=(0, 7))
        wrap_to_width(self.legend)

        totals = ttk.Frame(self)
        totals.pack(fill="x", pady=(0, 10))
        self.vectors = table(totals, ("Resource", "Total", "Allocated", "Available"),
                             (107, 85, 100, 100), height=3)
        ttk.Label(self, text="Process matrices", style="Accent.TLabel").pack(anchor="w", pady=(0, 4))
        self.matrices = table(self, ("Process", "Allocation", "Max", "Need"), (73, 111, 111, 111), height=5)

    def show(self, state, names, heading="Input state"):
        self.heading.configure(text=heading)
        if state is None:
            self.legend.configure(text="")
            fill_table(self.vectors, [])
            fill_table(self.matrices, [])
            return

        self.legend.configure(text=f"Resource order · {', '.join(names)}\n"
                                   "Available = Total - Allocated. Need = Max - Allocation.")
        fill_table(self.vectors, [
            (name, total, total - available, available)
            for name, total, available in zip(names, state.total, state.available)
        ])
        rows = [
            (f"P{index}", vector_text(held), vector_text(maximum), vector_text(need))
            for index, (held, maximum, need) in enumerate(zip(state.allocation, state.maximum, state.need))
        ]
        table_font = font.nametofont("TkDefaultFont")
        for index, column in enumerate(("Allocation", "Max", "Need"), 1):
            width = max(111, 16 + max(table_font.measure(row[index]) for row in rows))
            self.matrices.column(column, width=width, minwidth=width)
        fill_table(self.matrices, rows)


class TraceView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=9)
        self.heading = ttk.Label(self, style="Heading.TLabel")
        self.heading.pack(fill="x", pady=(0, 4))
        self.initial = ttk.Label(self, style="Muted.TLabel", wraplength=500, justify="left")
        self.initial.pack(fill="x", pady=(0, 5))
        self.final = ttk.Label(self, style="Accent.TLabel", wraplength=500, justify="left")
        self.final.pack(fill="x", pady=(0, 7))
        wrap_to_width(self.initial)
        wrap_to_width(self.final)
        self.checks = table(
            self, ("#", "Process", "Need", "Work before", "Need <= Work", "Released", "Work after", "Finish"),
            (40, 72, 85, 99, 100, 85, 99, 112), height=6,
        )

    def show(self, result, names):
        if result is None:
            self.heading.configure(text="Run a safety check to see the trace.", style="Heading.TLabel")
            self.initial.configure(text="")
            self.final.configure(text="")
            fill_table(self.checks, [])
            return

        sequence = " -> ".join(f"P{index}" for index in result.sequence)
        self.heading.configure(text="SAFE STATE" if result.safe else "UNSAFE STATE",
                               style="Accent.TLabel" if result.safe else "Alert.TLabel")
        self.initial.configure(
            text=f"Resource order · {', '.join(names)}\n"
                 f"Start Work = Available = {vector_text(result.initial_work)}\n"
                 f"Start Finish {flags_text([False] * len(result.finish))} · P0 onward",
        )
        if result.safe:
            summary = f"Safe sequence · {sequence}"
        else:
            summary = "No unfinished process can proceed."
            if sequence:
                summary += f" Finished during simulation · {sequence}"
        self.final.configure(text=f"{summary}\n"
                                  f"Final Work {vector_text(result.work)}   Finish {flags_text(result.finish)}")
        rows = [
            (step, f"P{check.process}", vector_text(check.need), vector_text(check.before),
             comparison_text(check.blocking, names),
             vector_text(check.released) if check.released is not None else "-",
             vector_text(check.after), flags_text(check.finish))
            for step, check in enumerate(result.checks, 1)
        ]
        table_font = font.nametofont("TkDefaultFont")
        for index, (column, base) in enumerate(
            zip(("Need", "Work before", "Need <= Work", "Released", "Work after", "Finish"),
                (85, 99, 100, 85, 99, 112)), 2
        ):
            width = max(base, 14 + max(table_font.measure(row[index]) for row in rows))
            self.checks.column(column, width=width, minwidth=width)
        fill_table(self.checks, rows)


class BankersTab(LabPanel):
    def __init__(self, master):
        super().__init__(master)
        self._build_inputs()
        self._build_results()
        self.load_example(SAFE_EXAMPLE)

    def _build_inputs(self):
        panel = ttk.Frame(self.body, padding=13)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(panel, text="01   Resource snapshot", style="Heading.TLabel").pack(anchor="w")

        counts = ttk.Frame(panel)
        counts.pack(fill="x", pady=(8, 7))
        self.process_count = tk.StringVar(master=self)
        self.resource_count = tk.StringVar(master=self)
        ttk.Label(counts, text="Processes").pack(side="left")
        ttk.Spinbox(counts, from_=1, to=MAX_PROCESSES, textvariable=self.process_count,
                    width=5).pack(side="left", padx=(5, 14))
        ttk.Label(counts, text="Resource types").pack(side="left")
        ttk.Spinbox(counts, from_=1, to=MAX_RESOURCES, textvariable=self.resource_count,
                    width=5).pack(side="left", padx=(5, 0))

        fields = ttk.Frame(panel)
        fields.pack(fill="x")
        fields.columnconfigure(1, weight=1)
        self.names = tk.StringVar(master=self)
        self.total = tk.StringVar(master=self)
        for row, (label, variable) in enumerate((("Names (optional)", self.names), ("Total vector", self.total))):
            ttk.Label(fields, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(fields, textvariable=variable, width=17).grid(row=row, column=1, sticky="ew", padx=(7, 0))

        ttk.Label(panel, text="One row per process, starting at P0.\nUse spaces or commas in each row.",
                  style="Muted.TLabel", justify="left").pack(anchor="w", pady=(7, 4))
        matrices = ttk.Frame(panel)
        matrices.pack(fill="both", expand=True)
        matrices.rowconfigure(1, weight=1)
        for column in range(2):
            matrices.columnconfigure(column, weight=1, uniform="matrix")
        ttk.Label(matrices, text="Allocation", style="Accent.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(matrices, text="Max", style="Accent.TLabel").grid(row=0, column=1, sticky="w", padx=(6, 0))
        allocation_frame, self.allocation = input_text(matrices, width=14, height=5)
        maximum_frame, self.maximum = input_text(matrices, width=14, height=5)
        allocation_frame.grid(row=1, column=0, sticky="nsew")
        maximum_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        actions = ttk.Frame(panel)
        actions.pack(fill="x", pady=(7, 9))
        ttk.Button(actions, text="Check safety", style="Primary.TButton", command=self.evaluate).pack(side="left")
        ttk.Button(actions, text="Safe example", command=lambda: self.load_example(SAFE_EXAMPLE)).pack(side="left", padx=5)
        ttk.Button(actions, text="Unsafe example", command=lambda: self.load_example(UNSAFE_EXAMPLE)).pack(side="left")

        ttk.Separator(panel).pack(fill="x", pady=(0, 7))
        ttk.Label(panel, text="Optional resource request", style="Accent.TLabel").pack(anchor="w")
        request_row = ttk.Frame(panel)
        request_row.pack(fill="x", pady=(3, 2))
        self.request_pid = tk.StringVar(master=self)
        self.request_values = tk.StringVar(master=self)
        ttk.Label(request_row, text="Process").pack(side="left")
        ttk.Entry(request_row, textvariable=self.request_pid, width=5).pack(side="left", padx=(4, 9))
        ttk.Label(request_row, text="Vector").pack(side="left")
        ttk.Entry(request_row, textvariable=self.request_values, width=11).pack(side="left", padx=(4, 0),
                                                                                fill="x", expand=True)
        ttk.Button(panel, text="Check request", command=lambda: self.evaluate(request=True)).pack(anchor="w", pady=(3, 0))

    def _build_results(self):
        panel = ttk.Frame(self.body, padding=13)
        panel.grid(row=0, column=1, sticky="nsew")
        ttk.Label(panel, text="02   Results", style="Heading.TLabel").pack(anchor="w", pady=(0, 7))
        self.tabs = ttk.Notebook(panel)
        self.tabs.pack(fill="both", expand=True)
        self.state = StateView(self.tabs)
        self.trace = TraceView(self.tabs)
        self.request_tab = ttk.Frame(self.tabs, padding=9)
        self.tabs.add(self.state, text="Matrices")
        self.tabs.add(self.trace, text="Safety trace")
        self.tabs.add(self.request_tab, text="Request result")

        self.decision = ttk.Label(self.request_tab, style="Heading.TLabel", wraplength=505)
        self.decision.pack(fill="x", pady=(0, 4))
        self.request_checks = ttk.Label(self.request_tab, style="Muted.TLabel", wraplength=505, justify="left")
        self.request_checks.pack(fill="x", pady=(0, 7))
        wrap_to_width(self.decision)
        wrap_to_width(self.request_checks)
        self.tentative_tabs = ttk.Notebook(self.request_tab)
        self.tentative_tabs.pack(fill="both", expand=True)
        self.tentative_state = StateView(self.tentative_tabs)
        self.tentative_trace = TraceView(self.tentative_tabs)
        self.tentative_tabs.add(self.tentative_state, text="Tentative matrices")
        self.tentative_tabs.add(self.tentative_trace, text="Tentative safety trace")

    def load_example(self, example):
        count, width, names, total, allocation, maximum, pid, request = example
        self.process_count.set(str(count))
        self.resource_count.set(str(width))
        self.names.set(names)
        self.total.set(total)
        set_text(self.allocation, allocation)
        set_text(self.maximum, maximum)
        self.request_pid.set(pid)
        self.request_values.set(request)
        self.evaluate()

    def read_state(self):
        count = read_integer(self.process_count.get(), "Process count", 1, MAX_PROCESSES)
        width = read_integer(self.resource_count.get(), "Resource type count", 1, MAX_RESOURCES)
        names = tuple(cells(self.names.get())) or tuple(f"R{index}" for index in range(1, width + 1))
        if len(names) != width or len(set(names)) != width or any(
            not name or len(name) > 16 or any(char.isspace() for char in name) for name in names
        ):
            raise ValueError(f"Enter {width} unique resource names, up to 16 characters each, or leave them blank.")
        state = BankState(
            read_vector(self.total.get(), "Total", width),
            read_matrix(self.allocation.get("1.0", "end-1c"), "Allocation", count, width),
            read_matrix(self.maximum.get("1.0", "end-1c"), "Max", count, width),
        )
        return state, names

    def evaluate(self, request=False):
        try:
            state, names = self.read_state()
            request_result = None
            if request:
                pid = re.fullmatch(r"[Pp]([0-9]{1,2})", self.request_pid.get().strip())
                if pid is None:
                    raise ValueError("Enter the requesting process as P0, P1, and so on.")
                vector = read_vector(self.request_values.get(), "Request", len(names))
                request_result = check_request(state, int(pid[1]), vector)
        except ValueError as error:
            self.state.show(None, (), "Enter a valid snapshot to see the matrices.")
            self.trace.show(None, ())
            self.show_request(None, ())
            self.feedback(str(error), error=True)
            return

        self.state.show(state, names)
        self.trace.show(check_safety(state), names)
        self.show_request(request_result, names)
        self.tabs.select(self.request_tab if request else self.trace)
        self.feedback(f"Checked {len(state.allocation)} processes and {len(names)} resource types. "
                      "Run again after editing the snapshot.")

    def show_request(self, result, names):
        if result is None:
            self.decision.configure(text="Enter a process and vector to check a request.", style="Heading.TLabel")
            self.request_checks.configure(text="")
            self.tentative_state.show(None, (), "Run a request check to see tentative matrices.")
            self.tentative_trace.show(None, ())
            return

        self.decision.configure(text=f"{result.decision} · P{result.process}",
                                style="Accent.TLabel" if result.decision == "GRANT" else "Alert.TLabel")
        safety = "Skipped after prechecks"
        if result.safety is not None:
            safety = "SAFE STATE" if result.safety.safe else "UNSAFE STATE"
        self.request_checks.configure(
            text=f"Request {vector_text(result.request)} <= Need {vector_text(result.need)}"
                 f" · {comparison_text(result.over_need, names)}\n"
                 f"Request {vector_text(result.request)} <= Available {vector_text(result.available)}"
                 f" · {comparison_text(result.over_available, names)}\n"
                 f"Safety result · {safety}\n{result.explanation}",
        )
        heading = "Tentative state" if result.tentative else "Tentative state skipped after prechecks."
        self.tentative_state.show(result.tentative, names, heading)
        self.tentative_trace.show(result.safety, names)
        self.tentative_tabs.select(self.tentative_state)