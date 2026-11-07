"""class PageTab - the 'Page Replacement' page: inputs, frame table and the
step-by-step explanation.
"""

from tkinter import messagebox

import customtkinter as ctk

from canvas_card import CanvasCard
from compare_window import CompareWindow
from helpers import draw_table, output_textbox, read_int, set_text, split_tokens, two_dp, write_text
from input_panel import InputPanel, input_textbox
from page_algorithms import PAGE_ALGORITHMS, solve_pages
from stat_card import StatCard
from stepper import Stepper
from theme import C, CFONT, FONT, MAX_FRAMES, P, px, segment_style


class PageTab(ctk.CTkFrame):
    EXAMPLE = {"refs": "7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1",
               "frames": "3"}
    EMPTY_MESSAGE = ("Enter a reference string and the number of frames,\n"
                     "choose an algorithm, then click Solve.")

    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.result = None
        self.message = self.EMPTY_MESSAGE
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._build_inputs()
        self._build_outputs()
        self._algorithm_changed()
        self.load_example()

    # ----- layout ---------------------------------------------------------
    def _build_inputs(self):
        p = InputPanel(self, "Page Replacement")
        p.grid(row=0, column=0, sticky="ns", padx=(16, 12), pady=16)

        p.label("Reference string", span=1, top=10, hint="spaces or commas")
        p.next_row()
        self.refs_box = p.put(input_textbox(p))
        p.next_row()

        p.label("Number of frames")
        p.next_row()
        self.frames = p.put(Stepper(p, 1, MAX_FRAMES, command=self._auto_solve), sticky="w")
        p.next_row()

        p.label("Algorithm")
        p.next_row()
        self.algorithm = p.put(ctk.CTkSegmentedButton(
            p, values=list(PAGE_ALGORITHMS), command=self._algorithm_changed,
            width=InputPanel.WIDTH, dynamic_resizing=False, **segment_style()))
        self.algorithm.set("FIFO")
        p.next_row()
        self.description = p.put(p.description(), top=6)
        p.next_row()

        p.buttons(self.solve, self.compare, self.load_example, self.clear)

        for widget in (self.refs_box, self.frames.entry):
            widget.bind("<Return>", self.solve)

    def _build_outputs(self):
        out = ctk.CTkFrame(self, fg_color="transparent")
        out.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        out.columnconfigure(0, weight=1)
        out.rowconfigure(1, weight=3)
        out.rowconfigure(2, weight=2)

        stats = ctk.CTkFrame(out, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew")
        self.card_faults = StatCard(stats, "Page faults", "fault_fg")
        self.card_hits = StatCard(stats, "Page hits", "hit_fg")
        self.card_fault_rate = StatCard(stats, "Fault rate")
        self.card_hit_rate = StatCard(stats, "Hit rate")
        self.stat_cards = (self.card_faults, self.card_hits, self.card_fault_rate,
                           self.card_hit_rate)
        for i, card in enumerate(self.stat_cards):
            stats.columnconfigure(i, weight=1, uniform="stats")
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))

        self.table = CanvasCard(out, "Frame table", legend=[
            ("box", "fault_bg", "F = page fault (page loaded)"),
            ("box", "hit_bg", "H = hit (already in memory)")])
        self.table.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.table.on_resize = self.draw_table

        explain_card = ctk.CTkFrame(out, corner_radius=12, fg_color=C("card"))
        explain_card.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        explain_card.rowconfigure(1, weight=1)
        explain_card.columnconfigure(0, weight=1)
        ctk.CTkLabel(explain_card, text="Step-by-step explanation", font=FONT.bold,
                     text_color=C("text"), height=22).grid(row=0, column=0, sticky="w",
                                                           padx=14, pady=(10, 2))
        self.explanation = output_textbox(explain_card, wrap="none")
        self.explanation.grid(row=1, column=0, sticky="nsew", padx=(6, 4), pady=(0, 10))

    # ----- events ---------------------------------------------------------
    def _algorithm_changed(self, choice=None):
        self.description.configure(text=PAGE_ALGORITHMS[self.algorithm.get()][1])
        if choice is not None:
            self._auto_solve()

    def _auto_solve(self, *_):
        if self.refs_box.get("1.0", "end").strip():
            self.solve(quiet=True)

    def load_example(self):
        """Textbook example (Silberschatz): 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1."""
        set_text(self.refs_box, self.EXAMPLE["refs"])
        self.frames.set(self.EXAMPLE["frames"])
        self.solve()

    def clear(self):
        set_text(self.refs_box, "")
        self.frames.set("3")
        self._clear_results(self.EMPTY_MESSAGE)
        self.refs_box.focus_set()

    # ----- solving ----------------------------------------------------------
    def _read_inputs(self):
        tokens = split_tokens(self.refs_box.get("1.0", "end"))
        if not tokens:
            raise ValueError("Please enter the reference string, for example: 7 0 1 2 0 3 0 4")
        refs = [str(int(t)) if t.isdigit() else t for t in tokens]   # "07" -> "7"
        frames = read_int(self.frames.get(), "number of frames", 1, MAX_FRAMES)
        return refs, frames

    def solve(self, event=None, quiet=False):
        """Read the inputs, run the chosen algorithm and show the results."""
        try:
            refs, frames = self._read_inputs()
        except ValueError as error:
            if quiet:
                self._clear_results(f"Check the input:\n{error}")
            else:
                messagebox.showerror("Please check your input", str(error), parent=self)
            return "break"
        self.result = solve_pages(self.algorithm.get(), refs, frames)
        self._show_results()
        return "break"

    def compare(self):
        """Run FIFO, LRU and Optimal on the same input and compare them."""
        try:
            refs, frames = self._read_inputs()
        except ValueError as error:
            messagebox.showerror("Please check your input", str(error), parent=self)
            return
        results = [solve_pages(name, refs, frames) for name in PAGE_ALGORITHMS]
        subtitle = (f"Reference string: {' '.join(refs)}\n"
                    f"{len(refs)} references   •   {frames} frames")
        CompareWindow(
            self, "Page replacement: all algorithms", subtitle, "faults",
            bars=[(r.algorithm, r.faults) for r in results],
            headers=["Algorithm", "Page faults", "Page hits", "Fault rate", "Hit rate"],
            rows=[[r.algorithm, r.faults, r.hits, f"{two_dp(r.fault_rate)}%",
                   f"{two_dp(r.hit_rate)}%"] for r in results],
            align=["w", "center", "center", "center", "center"], stretch="all")

    # ----- showing the results -----------------------------------------------
    def _clear_results(self, message):
        self.result = None
        self.message = message
        for card in self.stat_cards:
            card.show("-")
        write_text(self.explanation, [])
        self.draw_table()

    def _show_results(self):
        r = self.result
        total = len(r.refs)
        self.card_faults.show(str(r.faults), f"out of {total} references")
        self.card_hits.show(str(r.hits), f"out of {total} references")
        self.card_fault_rate.show(f"{two_dp(r.fault_rate)}%",
                                  f"{r.faults} ÷ {total} × 100")
        self.card_hit_rate.show(f"{two_dp(r.hit_rate)}%", f"{r.hits} ÷ {total} × 100")
        self._fill_explanation()
        self.draw_table()

    def refresh_theme(self):
        """Redraw everything that is not a CustomTkinter widget (after a theme change)."""
        self.table.refresh_theme()
        if self.result is not None:
            self._show_results()
        else:
            self._clear_results(self.message)

    def _fill_explanation(self):
        r = self.result

        def frames_text(frames):
            return "[" + ", ".join("-" if p is None else p for p in frames) + "]"

        frames_w = max([len("Frames after")] + [len(frames_text(s.frames)) for s in r.steps])
        page_w = max([4] + [len(p) for p in r.refs])
        total = len(r.refs)
        plural = "s" if r.n_frames != 1 else ""
        parts = [(f"{r.algorithm} with {r.n_frames} frame{plural}, {total} page references\n\n",
                  "h"),
                 (f"{'Step':>4}  {'Page':>{page_w}}  {'Result':<6}  "
                  f"{'Frames after':<{frames_w}}  Explanation\n", "b")]
        for i, s in enumerate(r.steps, 1):
            parts.append((f"{i:>4}  {s.page:>{page_w}}  ", None))
            parts.append((f"{'HIT' if s.hit else 'FAULT':<6}", "hit" if s.hit else "fault"))
            parts.append((f"  {frames_text(s.frames):<{frames_w}}  {s.reason}\n", None))
        parts += [
            ("\nPage faults = ", "b"), (str(r.faults), "fault"),
            ("     Page hits = ", "b"), (str(r.hits), "hit"),
            (f"     Total references = {total}\n", "b"),
            ("Fault rate = faults ÷ references × 100 = ", None),
            (f"{r.faults} ÷ {total} × 100 = {two_dp(r.fault_rate)}%\n", "answer"),
            ("Hit rate   = hits ÷ references × 100   = ", None),
            (f"{r.hits} ÷ {total} × 100 = {two_dp(r.hit_rate)}%\n", "answer"),
        ]
        write_text(self.explanation, parts)

    # ----- the frame table: the frames are the column headers -------------------
    def draw_table(self):
        card = self.table
        r = self.result
        if r is None:
            card.message(self.message)
            return
        c, _width, _height = card.start()
        n = r.n_frames
        headers = (["Step", "Reference"] + [f"Frame {j + 1}" for j in range(n)]
                   + ["Fault / Hit", "Replaced"])
        rows = [[i, s.page] + ["" if v is None else v for v in s.frames]
                + ["H" if s.hit else "F", s.victim or ""] for i, s in enumerate(r.steps, 1)]
        pal = P()

        def style(row, col):
            s = r.steps[row]
            if col == 0 or col == 3 + n:                     # step number, replaced page
                return {"fg": pal["muted"]}
            if col == 1:                                     # the page being referenced
                return {"bg": pal["accent_soft"], "fg": pal["accent_text"], "font": CFONT.bold}
            if col == 2 + n or col - 2 == s.slot:            # F/H, and the frame that was used
                key = "hit" if s.hit else "fault"
                return {"bg": pal[key + "_bg"], "fg": pal[key + "_fg"], "font": CFONT.bold}
            return None

        size = draw_table(c, headers, rows, style, min_width=px(64))
        card.finish(*size)
