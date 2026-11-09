"""Tkinter screen shared by the two CPU scheduling topics."""

import tkinter as tk
from tkinter import font, ttk

from cpu_core import INPUT_ORDER, MAX_JOBS, common_schedules, parse_workload
from lab_widgets import LabPanel, fill_table, input_text, set_text, table, wrap_to_width
from theme import P

PROCESS_COLORS = ("#16665e", "#245797", "#7c4a9b", "#a14c32", "#42673d", "#865519", "#385975", "#9b3c71")


class CPUView(LabPanel):
    def __init__(self, master):
        super().__init__(master)
        self.results = {}
        self.visible_result = None
        self._build_inputs()
        self._build_results()
        self.load_example()

    def _build_inputs(self):
        inputs = ttk.Frame(self.body, padding=13)
        inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(inputs, text="01   Workload", style="Heading.TLabel").pack(anchor="w")

        count_row = ttk.Frame(inputs)
        count_row.pack(fill="x", pady=(9, 7))
        ttk.Label(count_row, text="Number of processes").pack(side="left")
        self.count = tk.StringVar()
        ttk.Spinbox(count_row, from_=1, to=MAX_JOBS, width=6, textvariable=self.count).pack(side="right")

        columns = "ID   AT   BT   Priority" if self.with_priority else "ID   AT   BT"
        ttk.Label(inputs, text=columns, style="Accent.TLabel").pack(anchor="w")
        ttk.Label(inputs, text="One process per line. Use spaces or commas.",
                  style="Muted.TLabel", wraplength=260).pack(anchor="w", pady=(2, 4))
        editor, self.jobs = input_text(inputs, width=31, height=6)
        editor.pack(fill="both", expand=True, pady=(0, 8))

        options = ttk.Frame(inputs)
        options.pack(fill="x")
        options.columnconfigure(1, weight=1)
        self.build_options(options)

        buttons = ttk.Frame(inputs)
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Run all four", command=self.run_all,
                   style="Primary.TButton").pack(side="left", fill="x", expand=True)
        ttk.Button(buttons, text="Load example", command=self.load_example).pack(side="right", padx=(7, 0))

    def _build_results(self):
        output = ttk.Frame(self.body, padding=13)
        output.grid(row=0, column=1, sticky="nsew")
        ttk.Label(output, text="02   Results", style="Heading.TLabel").pack(anchor="w", pady=(0, 7))
        self.tabs = ttk.Notebook(output)
        self.tabs.pack(fill="both", expand=True)

        self.schedule_tab = ttk.Frame(self.tabs, padding=9)
        self.compare_tab = ttk.Frame(self.tabs, padding=9)
        self.tabs.add(self.schedule_tab, text="Schedule")
        self.tabs.add(self.compare_tab, text="Compare all")

        toolbar = ttk.Frame(self.schedule_tab)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Algorithm").pack(side="left")
        self.algorithm = ttk.Combobox(toolbar, state="readonly", width=18)
        self.algorithm.pack(side="left", padx=(7, 0))
        self.algorithm.bind("<<ComboboxSelected>>", lambda _: self.show_schedule())
        self.detail = ttk.Label(self.schedule_tab, style="Muted.TLabel", wraplength=485)
        self.detail.pack(fill="x", pady=(5, 1))
        self.averages = ttk.Label(self.schedule_tab, style="Accent.TLabel", wraplength=485)
        self.averages.pack(fill="x", pady=(0, 7))
        wrap_to_width(self.detail)
        wrap_to_width(self.averages)

        chart = ttk.Frame(self.schedule_tab)
        chart.pack(fill="x", pady=(0, 7))
        ttk.Label(chart, text="Gantt chart · time units", style="Heading.TLabel").pack(anchor="w")
        self.plot = tk.Canvas(chart, height=82, bg=P()["field"], highlightbackground=P()["border"],
                              highlightthickness=1)
        scrollbar = ttk.Scrollbar(chart, orient="horizontal", command=self.plot.xview)
        self.plot.configure(xscrollcommand=scrollbar.set)
        self.plot.pack(fill="x", pady=(4, 0))
        scrollbar.pack(fill="x")
        self.plot.bind("<Configure>", lambda _: self.draw_chart())

        detail_tabs = ttk.Notebook(self.schedule_tab)
        detail_tabs.pack(fill="both", expand=True)
        metrics_frame = ttk.Frame(detail_tabs, padding=5)
        trace_frame = ttk.Frame(detail_tabs, padding=5)
        detail_tabs.add(metrics_frame, text="Process metrics")
        detail_tabs.add(trace_frame, text="Timeline steps")
        headings = ("Process", "AT", "BT")
        widths = (103, 56, 56)
        if self.with_priority:
            headings += ("Priority",)
            widths += (77,)
        self.metrics = table(metrics_frame, headings + ("CT", "TAT", "WT", "RT"),
                             widths + (58, 58, 58, 58), height=5)
        self.trace = table(trace_frame, ("Step", "Process", "Start", "End", "Ran", "Remaining BT"),
                           (52, 103, 68, 68, 61, 119), height=5)

        ttk.Label(self.compare_tab, text="Same workload, four policies", style="Heading.TLabel").pack(anchor="w")
        self.comparison = ttk.Label(self.compare_tab, style="Muted.TLabel", justify="left", wraplength=475)
        self.comparison.pack(fill="x", pady=(6, 9))
        wrap_to_width(self.comparison)
        self.comparison_table = table(self.compare_tab, ("Algorithm", "Avg TAT", "Avg WT", "Avg RT"),
                                      (145, 92, 92, 92), height=5)

    def tie_break(self):
        return INPUT_ORDER

    def load_example(self):
        set_text(self.jobs, self.example_rows)
        self.count.set(str(len(self.example_rows.splitlines())))
        self.restore_settings()
        self.run_all()

    def run_all(self):
        try:
            jobs = parse_workload(self.count.get(), self.jobs.get("1.0", "end-1c"), self.with_priority)
            extra = self.extra_schedule(jobs)
            results = common_schedules(jobs, self.tie_break()) + [extra]
        except ValueError as error:
            self.results = {}
            self.algorithm.configure(values=())
            self.algorithm.set("")
            self.show_schedule()
            self.show_comparison()
            self.feedback(str(error), error=True)
            return

        selected = self.algorithm.get()
        self.results = {result.name: result for result in results}
        self.algorithm.configure(values=tuple(self.results))
        self.algorithm.set(selected if selected in self.results else results[0].name)
        self.show_schedule()
        self.show_comparison()
        self.feedback(f"Calculated four policies for {len(jobs)} processes. Run again after editing the workload or settings.")

    def show_schedule(self):
        result = self.results.get(self.algorithm.get())
        self.visible_result = result
        self.draw_chart()
        if result is None:
            self.detail.configure(text="Enter a valid workload to see a schedule.")
            self.averages.configure(text="")
            fill_table(self.metrics, [])
            fill_table(self.trace, [])
            return

        self.detail.configure(text=result.detail)
        tat, wt, rt = result.averages
        self.averages.configure(text=f"Avg TAT  {tat:.2f}     Avg WT  {wt:.2f}     Avg RT  {rt:.2f}")
        rows = []
        for metric in result.metrics:
            job = metric.process
            row = [job.pid, job.arrival, job.burst]
            if self.with_priority:
                row.append(job.priority)
            rows.append(row + [metric.completion, metric.turnaround, metric.waiting, metric.response])
        fill_table(self.metrics, rows)
        fill_table(self.trace, [
            (index, segment.pid or "Idle", segment.start, segment.end,
             segment.end - segment.start, "-" if segment.remaining is None else segment.remaining)
            for index, segment in enumerate(result.slices, 1)
        ])

    def show_comparison(self):
        results = list(self.results.values())
        values = [(result.name, result.averages) for result in results]
        fill_table(self.comparison_table, [(name, *(f"{value:.2f}" for value in averages))
                                           for name, averages in values])
        if not results:
            self.comparison.configure(text="Run a valid workload to compare the four policies.")
            return

        lines = [results[-1].detail]
        for index, label in enumerate(("turnaround", "waiting", "response")):
            best = min(averages[index] for _, averages in values)
            winners = ", ".join(name for name, averages in values if averages[index] == best)
            lines.append(f"Lowest average {label} · {winners} ({best:.2f})")
        self.comparison.configure(text="\n".join(lines))

    def refresh_theme(self):
        super().refresh_theme()
        self.draw_chart()

    def draw_chart(self):
        p = P()
        self.plot.configure(bg=p["field"], highlightbackground=p["border"])
        self.plot.delete("all")
        result = self.visible_result
        if result is None:
            self.plot.configure(scrollregion=(0, 0, 1, 82))
            return

        timeline = result.slices
        colors = {row.process.pid: PROCESS_COLORS[index % len(PROCESS_COLORS)]
                  for index, row in enumerate(result.metrics)}
        horizon = timeline[-1].end
        text_font = font.nametofont("TkDefaultFont")
        margin = max(30, text_font.measure(str(horizon)) // 2 + 10)
        span = max(self.plot.winfo_width() - 2 * margin - 3, min(7200, len(timeline) * 78))
        self.plot.configure(scrollregion=(0, 0, span + 2 * margin, 82))
        self.plot.xview_moveto(0)

        def x(time):
            return margin + span * time / horizon

        last_label_end = -100
        final_label_start = x(horizon) - text_font.measure(str(horizon)) / 2
        for segment in timeline:
            left, right = x(segment.start), x(segment.end)
            color = colors.get(segment.pid, "#657689")
            self.plot.create_rectangle(left, 10, right, 48, fill=color, width=0)
            label = segment.pid or "Idle"
            if right - left >= text_font.measure(label) + 8:
                self.plot.create_text((left + right) / 2, 29, text=label, fill="white", font=text_font)
            self.plot.create_line(left, 49, left, 56, fill=p["muted"])
            start_text = str(segment.start)
            half = text_font.measure(start_text) / 2
            if left - half > last_label_end + 5 and left + half < final_label_start - 5:
                self.plot.create_text(left, 68, text=start_text, fill=p["text"], font=text_font)
                last_label_end = left + half

        end_x = x(horizon)
        self.plot.create_line(end_x, 49, end_x, 56, fill=p["muted"])
        self.plot.create_text(end_x, 68, text=str(horizon), fill=p["text"], font=text_font)