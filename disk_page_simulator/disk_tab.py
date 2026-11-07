"""class DiskTab - the 'Disk Scheduling' page: inputs, graph, table of moves
and the written solution.
"""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from canvas_card import CanvasCard
from compare_window import CompareWindow
from disk_algorithms import CIRCULAR_ALGORITHMS, DIRECTION_ALGORITHMS, DISK_ALGORITHMS, solve_disk
from helpers import (_pull_back, _sign, draw_table, fmt, output_textbox, read_int, set_entry,
                     set_text, split_tokens, two_dp, write_text)
from input_panel import InputPanel, input_textbox
from page_algorithms import INF
from stat_card import StatCard
from theme import C, CFONT, DIRECTION_LABELS, FONT, P, entry_style, option_style, px, segment_style


class DiskTab(ctk.CTkFrame):
    EXAMPLE = {"queue": "98, 183, 37, 122, 14, 124, 65, 67", "head": "53", "cylinders": "200"}
    EMPTY_MESSAGE = ("Enter the request queue and the starting head position,\n"
                     "choose an algorithm, then click Solve.")

    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.result = None
        self.seek_rate = None
        self.message = self.EMPTY_MESSAGE
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._build_inputs()
        self._build_outputs()
        self._algorithm_changed()
        self.load_example()

    # ----- layout ---------------------------------------------------------
    def _build_inputs(self):
        p = InputPanel(self, "Disk Scheduling")
        p.grid(row=0, column=0, sticky="ns", padx=(16, 12), pady=16)

        p.label("Request queue", span=1, top=10, hint="spaces or commas")
        p.next_row()
        self.queue_box = p.put(input_textbox(p))
        p.next_row()

        p.label("Head starts at", column=0, span=1)
        p.label("Total cylinders", column=1, span=1)
        p.next_row()
        self.head_entry = p.put(ctk.CTkEntry(p, placeholder_text="e.g. 53", **entry_style()),
                                column=0, span=1)
        self.cylinders_entry = p.put(ctk.CTkEntry(p, placeholder_text="e.g. 200",
                                                  **entry_style()), column=1, span=1)
        p.next_row()

        p.label("Algorithm")
        p.next_row()
        self.algo_var = tk.StringVar(value="FCFS")
        p.put(ctk.CTkOptionMenu(p, values=list(DISK_ALGORITHMS), variable=self.algo_var,
                                command=self._algorithm_changed, width=InputPanel.WIDTH,
                                **option_style()))
        p.next_row()
        self.description = p.put(p.description(), top=6)
        p.next_row()

        p.label("Head direction")
        p.next_row()
        self.direction = p.put(ctk.CTkSegmentedButton(
            p, values=list(DIRECTION_LABELS.values()), command=lambda _value: self._auto_solve(),
            width=InputPanel.WIDTH, dynamic_resizing=False, **segment_style()))
        self.direction.set(DIRECTION_LABELS["up"])
        p.next_row()
        self.count_return_var = tk.BooleanVar(value=True)
        self.return_switch = p.put(ctk.CTkSwitch(
            p, text="Count the return jump", variable=self.count_return_var, onvalue=True,
            offvalue=False, command=self._auto_solve, font=FONT.ui, text_color=C("text"),
            progress_color=C("accent")), top=8, sticky="w")
        p.next_row()

        p.put(ctk.CTkLabel(p, text="Seek time per\ncylinder (ms)", font=FONT.bold,
                           text_color=C("text"), justify="left", anchor="w"),
              column=0, span=1, top=10, sticky="w")
        self.rate_entry = p.put(ctk.CTkEntry(p, placeholder_text="optional", **entry_style()),
                                column=1, span=1, top=10)
        p.next_row()

        p.buttons(self.solve, self.compare, self.load_example, self.clear)

        for widget in (self.queue_box, self.head_entry, self.cylinders_entry, self.rate_entry):
            widget.bind("<Return>", self.solve)

    def _build_outputs(self):
        out = ctk.CTkFrame(self, fg_color="transparent")
        out.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        out.columnconfigure(0, weight=1)
        out.rowconfigure(1, weight=3)
        out.rowconfigure(2, weight=2)

        stats = ctk.CTkFrame(out, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew")
        self.card_total = StatCard(stats, "Total head movement", "accent_text")
        self.card_average = StatCard(stats, "Average seek length")
        self.card_time = StatCard(stats, "Total seek time")
        self.stat_cards = (self.card_total, self.card_average, self.card_time)
        for i, card in enumerate(self.stat_cards):
            stats.columnconfigure(i, weight=1, uniform="stats")
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))

        self.graph = CanvasCard(out, "Head movement graph", legend=[
            ("dot", "start", "start"), ("dot", "accent", "request"),
            ("ring", "edge", "end of disk"), ("dash", "edge", "return jump")])
        self.graph.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.graph.on_resize = self.draw_chart

        bottom = ctk.CTkFrame(out, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        bottom.rowconfigure(0, weight=1)
        bottom.columnconfigure(0, weight=4, uniform="bottom")
        bottom.columnconfigure(1, weight=5, uniform="bottom")
        self.moves = CanvasCard(bottom, "Head movements")
        self.moves.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.moves.on_resize = self.draw_moves

        solution_card = ctk.CTkFrame(bottom, corner_radius=12, fg_color=C("card"))
        solution_card.grid(row=0, column=1, sticky="nsew")
        solution_card.rowconfigure(1, weight=1)
        solution_card.columnconfigure(0, weight=1)
        ctk.CTkLabel(solution_card, text="Solution", font=FONT.bold, text_color=C("text"),
                     height=22).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))
        self.solution = output_textbox(solution_card, wrap="word")
        self.solution.grid(row=1, column=0, sticky="nsew", padx=(6, 4), pady=(0, 10))

    # ----- events ---------------------------------------------------------
    def _algorithm_changed(self, choice=None):
        name = self.algo_var.get()
        self.description.configure(text=DISK_ALGORITHMS[name][1])
        self.direction.configure(state="normal" if name in DIRECTION_ALGORITHMS else "disabled")
        self.return_switch.configure(state="normal" if name in CIRCULAR_ALGORITHMS
                                     else "disabled")
        if choice is not None:
            self._auto_solve()

    def _auto_solve(self, *_):
        """Solve again right away when the algorithm or direction is changed."""
        if self.queue_box.get("1.0", "end").strip():
            self.solve(quiet=True)

    def _direction(self):
        return "down" if self.direction.get() == DIRECTION_LABELS["down"] else "up"

    def load_example(self):
        """Textbook example (Silberschatz): queue 98 183 37 122 14 124 65 67, head 53."""
        set_text(self.queue_box, self.EXAMPLE["queue"])
        set_entry(self.head_entry, self.EXAMPLE["head"])
        set_entry(self.cylinders_entry, self.EXAMPLE["cylinders"])
        set_entry(self.rate_entry, "")
        self.solve()

    def clear(self):
        set_text(self.queue_box, "")
        set_entry(self.head_entry, "")
        set_entry(self.cylinders_entry, "200")
        set_entry(self.rate_entry, "")
        self._clear_results(self.EMPTY_MESSAGE)
        self.queue_box.focus_set()

    # ----- solving ----------------------------------------------------------
    def _read_inputs(self):
        cylinders = read_int(self.cylinders_entry.get(), "total number of cylinders", 2)
        last = cylinders - 1
        head = read_int(self.head_entry.get(), "starting head position", 0, last)
        tokens = split_tokens(self.queue_box.get("1.0", "end"))
        if not tokens:
            raise ValueError("Please enter the request queue, for example: 98, 183, 37, 122")
        requests = []
        for token in tokens:
            try:
                cylinder = int(token)
            except ValueError:
                raise ValueError(f"'{token}' in the request queue is not a whole number.") from None
            if not 0 <= cylinder <= last:
                raise ValueError(f"Request {cylinder} is outside the disk.\n"
                                 f"With {cylinders} cylinders, valid numbers are 0 to {last}.")
            requests.append(cylinder)
        rate = None
        rate_text = self.rate_entry.get().strip()
        if rate_text:
            try:
                rate = float(rate_text)
            except ValueError:
                raise ValueError("The seek time per cylinder must be a number "
                                 "(or leave it blank).") from None
            if not 0 <= rate < INF:
                raise ValueError("The seek time per cylinder must be zero or more.")
        return requests, head, last, rate

    def solve(self, event=None, quiet=False):
        """Read the inputs, run the chosen algorithm and show the results."""
        try:
            requests, head, last, rate = self._read_inputs()
        except ValueError as error:
            if quiet:
                self._clear_results(f"Check the input:\n{error}")
            else:
                messagebox.showerror("Please check your input", str(error), parent=self)
            return "break"
        self.result = solve_disk(self.algo_var.get(), requests, head, last,
                                 self._direction(), bool(self.count_return_var.get()))
        self.seek_rate = rate
        self._show_results()
        return "break"           # stops the Enter key from adding a new line

    def compare(self):
        """Run all six algorithms on the same input and compare them."""
        try:
            requests, head, last, _rate = self._read_inputs()
        except ValueError as error:
            messagebox.showerror("Please check your input", str(error), parent=self)
            return
        direction = self._direction()
        count_return = bool(self.count_return_var.get())
        results = [solve_disk(name, requests, head, last, direction, count_return)
                   for name in DISK_ALGORITHMS]
        moving = "toward higher cylinders" if direction == "up" else "toward 0"
        subtitle = (f"Queue: {', '.join(map(str, requests))}\n"
                    f"Head at {head}   •   cylinders 0 to {last}   •   "
                    f"SCAN/LOOK family moving {moving}   •   "
                    f"return jump {'counted' if count_return else 'not counted'}")
        CompareWindow(
            self, "Disk scheduling: all algorithms", subtitle, "cylinders",
            bars=[(r.algorithm, r.total) for r in results],
            headers=["Algorithm", "Total head movement", "Average seek", "Seek order"],
            rows=[[r.algorithm, r.total, two_dp(r.average), ", ".join(map(str, r.seek_order))]
                  for r in results],
            align=["w", "center", "center", "w"])

    # ----- showing the results -----------------------------------------------
    def _clear_results(self, message):
        self.result = None
        self.message = message
        for card in self.stat_cards:
            card.show("-")
        write_text(self.solution, [])
        self.draw_chart()
        self.draw_moves()

    def _show_results(self):
        r = self.result
        not_counted = any(not m.counted for m in r.moves)
        self.card_total.show(str(r.total), "cylinders" + ("  (return jump not counted)"
                                                          if not_counted else ""))
        self.card_average.show(two_dp(r.average),
                               f"cylinders per request ({len(r.requests)} requests)")
        if self.seek_rate is None:
            self.card_time.show("-", "enter a seek time per cylinder")
        else:
            self.card_time.show(f"{fmt(r.total * self.seek_rate)} ms",
                                f"{r.total} × {fmt(self.seek_rate)} ms")
        self._fill_solution()
        self.draw_chart()
        self.draw_moves()

    def refresh_theme(self):
        """Redraw everything that is not a CustomTkinter widget (after a theme change)."""
        self.graph.refresh_theme()
        if self.result is not None:
            self._show_results()
        else:
            self._clear_results(self.message)

    def _fill_solution(self):
        r = self.result
        uses_direction = r.algorithm in DIRECTION_ALGORITHMS
        heading = f"{r.algorithm}: head starts at {r.head}"
        if uses_direction:
            heading += ", moving " + ("toward higher cylinders" if r.direction == "up"
                                      else "toward cylinder 0")
        path = [str(r.head)] + [f"({m.end})" if m.target == "edge" else str(m.end)
                                for m in r.moves]
        counted = [m for m in r.moves if m.counted]

        parts = [(heading + "\n\n", "h"),
                 ("Head path\n", "b"),
                 ("  " + " → ".join(path) + "\n", None)]
        if any(m.target == "edge" for m in r.moves):
            parts.append(("  ( ) = end of the disk, no request is serviced there\n", "muted"))
        parts += [("\nSeek order (requests serviced)\n", "b"),
                  ("  " + ", ".join(map(str, r.seek_order)) + "\n", None),
                  ("\nTotal head movement = sum of every move\n", "b")]
        if counted:
            parts += [("  = " + " + ".join(f"|{m.end} - {m.start}|" for m in counted) + "\n", None),
                      ("  = " + " + ".join(str(m.distance) for m in counted) + "\n", None)]
        parts.append((f"  = {r.total} cylinders\n", "answer"))
        for m in r.moves:
            if not m.counted:
                parts.append((f"  (the return jump {m.start} → {m.end} = {m.distance} "
                              f"cylinders is not counted)\n", "muted"))

        sweeps = [s for s in r.sweeps() if s.counted and s.distance > 0]
        if uses_direction and sweeps:
            parts += [
                ("\nShortcut: add up each sweep of the head\n", "b"),
                ("  = " + " + ".join(f"({max(s.start, s.end)} - {min(s.start, s.end)})"
                                     for s in sweeps) + "\n", None),
                ("  = " + " + ".join(str(s.distance) for s in sweeps) + f" = {r.total}\n", None),
            ]
        parts += [("\nAverage seek length = total ÷ number of requests\n", "b"),
                  (f"  = {r.total} ÷ {len(r.requests)} = {two_dp(r.average)} cylinders\n",
                   None)]
        if self.seek_rate is not None:
            parts += [("\nTotal seek time = total head movement × time per cylinder\n", "b"),
                      (f"  = {r.total} × {fmt(self.seek_rate)} ms = "
                       f"{fmt(r.total * self.seek_rate)} ms\n", None)]
        write_text(self.solution, parts)

    # ----- the table of head movements ------------------------------------------
    def draw_moves(self):
        card = self.moves
        r = self.result
        if r is None:
            card.message("")
            return
        c, width, _height = card.start()
        rows, muted = [], set()
        for i, m in enumerate(r.moves, 1):
            if m.jump:
                note = "return jump" + ("" if m.counted else " (not counted)")
            elif m.target == "edge":
                note = "end of disk"
            else:
                note = ""
            if not m.counted:
                muted.add(len(rows))
            rows.append([i, m.start, m.end, m.distance if m.counted else f"({m.distance})", note])
        rows.append(["", "", "Total", r.total, ""])
        pal = P()

        def style(row, _col):
            if row == len(rows) - 1:
                return {"bg": pal["accent_soft"], "fg": pal["accent_text"], "font": CFONT.bold}
            if row in muted:
                return {"fg": pal["muted"]}
            return None

        size = draw_table(c, ["#", "From", "To", "Moved", "Note"], rows, style,
                          align=["center", "center", "center", "center", "w"],
                          fill_width=width - px(2))
        card.finish(*size)

    # ----- the graph ----------------------------------------------------------
    def draw_chart(self):
        """Draw the classic disk scheduling graph: cylinder numbers across the
        top, time going down, one row for every movement of the head."""
        card = self.graph
        r = self.result
        if r is None:
            card.message(self.message)
            return
        c, width, height = card.start()
        pal = P()
        points = [r.head] + [m.end for m in r.moves]   # head position after each move
        left, right = px(54), px(48)
        axis_y = px(42)
        first_row = axis_y + px(26)
        rows = len(points) - 1
        row_h = (height - first_row - px(22)) / max(rows, 1)
        row_h = max(px(22), min(px(46), row_h))
        content_h = first_row + rows * row_h + px(22)
        span = width - left - right

        def x_of(cylinder):
            return left + span * cylinder / r.last_cyl

        def y_of(row):
            return first_row + row * row_h

        # dotted guide lines + the cylinder axis along the top
        marks = sorted({0, r.last_cyl, r.head, *r.requests})
        for cylinder in marks:
            c.create_line(x_of(cylinder), axis_y, x_of(cylinder), content_h - px(10),
                          fill=pal["grid"], dash=(2, 3))
        c.create_line(left, axis_y, left + span, axis_y, fill=pal["text"])
        c.create_text(px(16), axis_y - px(11), text="step", font=CFONT.tiny, fill=pal["muted"])
        label_end = [-INF, -INF]            # labels go on 2 levels so they don't overlap
        for cylinder in marks:
            x = x_of(cylinder)
            text = str(cylinder)
            half = CFONT.tiny.measure(text) / 2
            c.create_line(x, axis_y - px(3), x, axis_y + px(3), fill=pal["text"])
            for level in (0, 1):
                if x - half > label_end[level] + px(3):
                    if cylinder == r.head:
                        color = pal["start_text"]
                    elif cylinder in (0, r.last_cyl):
                        color = pal["text"]
                    else:
                        color = pal["muted"]
                    c.create_text(x, axis_y - px(11) - level * px(13), text=text,
                                  font=CFONT.tiny, fill=color)
                    label_end[level] = x + half
                    break

        # one arrow for every movement of the head
        radius = px(5)
        for i, move in enumerate(r.moves):
            x1, y1 = x_of(move.start), y_of(i)
            x2, y2 = _pull_back(x1, y1, x_of(move.end), y_of(i + 1), radius + px(2))
            options = {"fill": pal["accent"], "width": px(2), "arrow": "last",
                       "arrowshape": (px(9), px(11), px(4))}
            if move.jump:
                options.update(fill=pal["edge"], dash=(6, 4))
            c.create_line(x1, y1, x2, y2, **options)

        # a dot (and its cylinder number) for every position of the head
        for i, cylinder in enumerate(points):
            x, y = x_of(cylinder), y_of(i)
            if i == 0:
                fill, outline, color = pal["start"], pal["card"], pal["start_text"]
            elif r.moves[i - 1].target == "edge":
                fill, outline, color = pal["card"], pal["edge"], pal["muted"]
            else:
                fill, outline, color = pal["accent"], pal["card"], pal["text"]
            c.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill,
                          outline=outline, width=2 if outline == pal["edge"] else 1)
            self._label_point(c, points, i, x, y, width, color)
            if i > 0:
                c.create_text(px(16), y, text=str(i), font=CFONT.tiny, fill=pal["muted"])
        card.finish(width, content_h)

    @staticmethod
    def _label_point(c, points, i, x, y, width, color):
        """Write the cylinder number beside its dot, on a side with no line."""
        came = _sign(points[i] - points[i - 1]) if i > 0 else 0          # +1 = moving right
        goes = _sign(points[i + 1] - points[i]) if i + 1 < len(points) else 0
        if came != -1 and goes != 1:
            side, dy = 1, 0                 # nothing on the right side
        elif came != 1 and goes != -1:
            side, dy = -1, 0                # nothing on the left side
        else:
            side, dy = came, -px(9)         # lines on both sides: put it above
        text = str(points[i])
        text_w = CFONT.label.measure(text)
        gap = px(9)
        if side == 1 and x + gap + text_w > width - px(4):
            side = -1
        elif side == -1 and x - gap - text_w < px(26):     # keep clear of step numbers
            side = 1
        c.create_text(x + side * gap, y + dy, text=text, font=CFONT.label, fill=color,
                      anchor="w" if side == 1 else "e")
