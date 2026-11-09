# Disk Scheduling & Page Replacement Simulator

A CustomTkinter desktop app that solves disk scheduling (FCFS, SSTF, SCAN, C-SCAN,
LOOK, C-LOOK) and page replacement (FIFO, LRU, Optimal) step by step.

## Install once

```
pip install customtkinter
```

## Run (inside this folder)

```
python main.py           # opens the app
python main.py --test    # checks the algorithms against textbook answers
```

Keep all the `.py` files together in the same folder.

## Files (one class per file)

| File | Contains |
|---|---|
| `main.py` | starts the program |
| `app.py` | `App` – the main window (header, page switcher, dark mode) |
| `disk_tab.py` | `DiskTab` – the Disk Scheduling page |
| `page_tab.py` | `PageTab` – the Page Replacement page |
| `compare_window.py` | `CompareWindow` – the "Compare all" pop-up |
| `input_panel.py` | `InputPanel` – the input panel on the left of each page |
| `canvas_card.py` | `CanvasCard` – a card with a drawing canvas (graph, tables) |
| `stat_card.py` | `StatCard` – a result box |
| `stepper.py` | `Stepper` – number box with − and + buttons |
| `legend.py` | `Legend` – the colour legend |
| `theme.py` | colours, fonts and widget styles |
| `helpers.py` | small helper functions |
| `disk_algorithms.py` | Part 1 – disk scheduling algorithms |
| `page_algorithms.py` | Part 2 – page replacement algorithms |
| `self_test.py` | the `--test` check |

# Operating Systems Simulator

A Python desktop app with five tabs in one window.

| Tab | What it covers |
|---|---|
| 1. Priority | FCFS, non-preemptive SJF, preemptive SRTF, and Priority Scheduling. |
| 2. Round Robin | FCFS, SJF, SRTF, and Round Robin. |
| 3. Page Replacement | FIFO, LRU, and Optimal with frame traces and hit and fault totals. |
| 4. Disk Scheduling | FCFS, SSTF, and SCAN with head movement and algorithm comparison. |
| 5. Banker's | Safety trace and optional resource-request check. |

## Set up and run on Windows

Install Python 3.10 or newer with Tkinter. Open PowerShell in the folder containing `main.py`.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --test
.\.venv\Scripts\python.exe main.py
```

## Simulator conventions

- Priority starts in non-preemptive mode with smaller priority numbers first. The form lets you choose the convention used in class.
- In Round Robin, an arrival at the end of a time slice joins the queue before the unfinished running process rejoins.
- Disk cylinders range from `0` to `total cylinders - 1`. SCAN travels to the selected boundary before reversing.
- Banker's request check tests a tentative allocation against the current input snapshot.
- Use the topic and algorithms assigned by your instructor when preparing a class submission.

## References

- Scheduling policies and timing metrics. [OSTEP Chapter 7](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- Priority modes and ranking conventions. [UIC CPU Scheduling notes](https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/6_CPU_Scheduling.html)
- Banker's safety and request algorithms. [UMass Amherst CS377](https://lass.cs.umass.edu/~shenoy/courses/fall15/lectures/Lec11.pdf)

OpenAI ChatGPT assisted with the implementation, merge walkthrough, and verification. Describe your own changes and checks using your course's required disclosure format.