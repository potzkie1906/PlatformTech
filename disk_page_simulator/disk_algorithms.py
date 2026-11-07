"""PART 1 - Disk scheduling algorithms: FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK.
Pure logic, no GUI code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


#  Every algorithm receives:
#     requests   list of cylinder numbers, in the order they arrived
#     head       cylinder where the read/write head starts
#     last_cyl   highest cylinder number (199 for a disk with 200 cylinders)
#     direction  "up" = toward higher cylinders, "down" = toward cylinder 0
#  and returns the list of head movements, in the order they happen.
#
#  Total head movement = the sum of the distances of all those movements.
@dataclass
class DiskMove:
    """One movement of the read/write head, e.g. from cylinder 53 to 98."""
    start: int
    end: int
    # target = "request": a request is serviced at `end`
    #          "edge":    the head only reaches the end of the disk (nothing serviced)
    target: str = "request"
    jump: bool = False        # True for the C-SCAN / C-LOOK return trip
    counted: bool = True      # False if the return trip is left out of the total

    @property
    def distance(self) -> int:
        return abs(self.end - self.start)


class _Head:
    """Small helper: moves the head and writes down every movement."""

    def __init__(self, start: int):
        self.pos = start
        self.moves: List[DiskMove] = []

    def go(self, cylinder: int, target: str = "request", jump: bool = False):
        if target == "edge" and cylinder == self.pos:
            return                                  # already at that end of the disk
        self.moves.append(DiskMove(self.pos, cylinder, target, jump))
        self.pos = cylinder


def _split(requests, head, direction):
    """Sort the queue into the requests below and above the head.
    A request exactly at the head's cylinder is serviced first (0 movement)."""
    if direction == "up":
        below = sorted(r for r in requests if r < head)
        above = sorted(r for r in requests if r >= head)
    else:
        below = sorted(r for r in requests if r <= head)
        above = sorted(r for r in requests if r > head)
    return below, above


def disk_fcfs(requests, head, last_cyl, direction):
    """FCFS - service the requests in the exact order they arrived."""
    h = _Head(head)
    for r in requests:
        h.go(r)
    return h.moves


def disk_sstf(requests, head, last_cyl, direction):
    """SSTF - always go to the pending request that is closest to the head.
    If two requests are equally close, the one that arrived first wins."""
    h = _Head(head)
    pending = list(requests)
    while pending:
        closest = min(range(len(pending)), key=lambda i: abs(pending[i] - h.pos))
        h.go(pending.pop(closest))
    return h.moves


def disk_scan(requests, head, last_cyl, direction):
    """SCAN (elevator) - sweep all the way to the END of the disk, then reverse."""
    below, above = _split(requests, head, direction)
    h = _Head(head)
    if direction == "up":
        for r in above:                 # going up:   53 -> 65 -> 67 -> ... -> 183
            h.go(r)
        h.go(last_cyl, "edge")          # keep going to the last cylinder (199)
        for r in reversed(below):       # come back:  37 -> 14
            h.go(r)
    else:
        for r in reversed(below):       # going down: 53 -> 37 -> 14
            h.go(r)
        h.go(0, "edge")                 # keep going to cylinder 0
        for r in above:                 # come back:  65 -> 67 -> ... -> 183
            h.go(r)
    return h.moves


def _return_and_continue(h, edge, remaining):
    """C-SCAN return trip: jump to the opposite end of the disk, then keep
    servicing the remaining requests in the same direction as before."""
    if remaining and remaining[0] == edge:      # a request sits right on that end
        h.go(remaining[0], jump=True)
        remaining = remaining[1:]
    else:
        h.go(edge, "edge", jump=True)
    for r in remaining:
        h.go(r)


def disk_cscan(requests, head, last_cyl, direction):
    """C-SCAN (circular SCAN) - sweep to the end, jump back to the other end,
    and continue in the SAME direction (requests are only served one way)."""
    below, above = _split(requests, head, direction)
    h = _Head(head)
    if direction == "up":
        for r in above:
            h.go(r)
        h.go(last_cyl, "edge")
        if below:
            _return_and_continue(h, 0, below)                   # 0 -> upward
    else:
        for r in reversed(below):
            h.go(r)
        h.go(0, "edge")
        if above:
            _return_and_continue(h, last_cyl, above[::-1])      # last -> downward
    return h.moves


def disk_look(requests, head, last_cyl, direction):
    """LOOK - like SCAN, but turn around at the last request
    instead of going all the way to the end of the disk."""
    below, above = _split(requests, head, direction)
    h = _Head(head)
    if direction == "up":
        for r in above:
            h.go(r)
        for r in reversed(below):
            h.go(r)
    else:
        for r in reversed(below):
            h.go(r)
        for r in above:
            h.go(r)
    return h.moves


def disk_clook(requests, head, last_cyl, direction):
    """C-LOOK - like C-SCAN, but only go as far as the last request,
    then jump straight to the farthest request on the other side."""
    below, above = _split(requests, head, direction)
    h = _Head(head)
    if direction == "up":
        for r in above:
            h.go(r)
        for i, r in enumerate(below):               # lowest request first
            h.go(r, jump=(i == 0))
    else:
        for r in reversed(below):
            h.go(r)
        for i, r in enumerate(reversed(above)):     # highest request first
            h.go(r, jump=(i == 0))
    return h.moves


# name -> (function, short description shown in the app)
DISK_ALGORITHMS = {
    "FCFS": (disk_fcfs, "First-Come, First-Served: serves requests in the order "
                        "they arrive. Simple and fair, but the head may zig-zag a lot."),
    "SSTF": (disk_sstf, "Shortest Seek Time First: always moves to the closest "
                        "pending request. Less movement, but far requests can starve."),
    "SCAN": (disk_scan, "Elevator: sweeps to the END of the disk serving requests "
                        "on the way, then reverses direction."),
    "C-SCAN": (disk_cscan, "Circular SCAN: sweeps to the end, jumps back to the other "
                           "end, then keeps serving in the same direction."),
    "LOOK": (disk_look, "Like SCAN, but turns around at the last request instead of "
                        "going all the way to the disk end."),
    "C-LOOK": (disk_clook, "Like C-SCAN, but only goes to the last request, then jumps "
                           "back to the farthest request on the other side."),
}


DIRECTION_ALGORITHMS = {"SCAN", "C-SCAN", "LOOK", "C-LOOK"}   # need a head direction


CIRCULAR_ALGORITHMS = {"C-SCAN", "C-LOOK"}                   # have a return jump


@dataclass
class Sweep:
    """A run of movements in one direction (used for the 'shortcut' working)."""
    start: int
    end: int
    direction: int      # +1 = up, -1 = down, 0 = no movement yet
    jump: bool
    counted: bool

    @property
    def distance(self) -> int:
        return abs(self.end - self.start)


@dataclass
class DiskResult:
    algorithm: str
    requests: List[int]
    head: int
    last_cyl: int
    direction: str
    moves: List[DiskMove]

    @property
    def total(self) -> int:
        """Total head movement (in cylinders)."""
        return sum(m.distance for m in self.moves if m.counted)

    @property
    def average(self) -> float:
        """Average seek length = total head movement / number of requests."""
        return self.total / len(self.requests)

    @property
    def seek_order(self) -> List[int]:
        """The requests in the order they were serviced."""
        return [m.end for m in self.moves if m.target == "request"]

    def sweeps(self) -> List[Sweep]:
        """Group the moves into sweeps, e.g. SCAN toward 0 has two sweeps:
        53 -> 0 and 0 -> 183, so total = (53 - 0) + (183 - 0)."""
        sweeps: List[Sweep] = []
        for m in self.moves:
            step = (m.end > m.start) - (m.end < m.start)
            prev = sweeps[-1] if sweeps else None
            if (prev is not None and not prev.jump and not m.jump
                    and (step == 0 or prev.direction in (0, step))):
                prev.end = m.end
                prev.direction = prev.direction or step
            else:
                sweeps.append(Sweep(m.start, m.end, step, m.jump, m.counted))
        return sweeps


def solve_disk(algorithm, requests, head, last_cyl, direction="up", count_return=True):
    """Run one disk scheduling algorithm and return a DiskResult."""
    function = DISK_ALGORITHMS[algorithm][0]
    moves = function(list(requests), head, last_cyl, direction)
    for m in moves:
        m.counted = count_return or not m.jump
    return DiskResult(algorithm, list(requests), head, last_cyl, direction, moves)
