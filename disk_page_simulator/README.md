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
