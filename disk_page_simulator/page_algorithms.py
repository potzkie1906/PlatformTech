"""PART 2 - Page replacement algorithms: FIFO, LRU, OPTIMAL.
Pure logic, no GUI code.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import List, Optional


#  Every algorithm receives the reference string (a list of page names) and the
#  number of frames. For every reference it records a PageStep: was it a hit or
#  a fault, what the frames look like afterwards, and WHY.
INF = math.inf


@dataclass
class PageStep:
    """What happened when one page of the reference string was requested."""
    page: str
    frames: List[Optional[str]]   # frame contents AFTER this reference (None = empty)
    hit: bool                     # True = page was already in memory
    slot: int                     # frame that was hit, or that got the new page
    victim: Optional[str]         # page that was removed (None = no replacement)
    reason: str                   # plain-English explanation


def _hit_step(page, frames):
    return PageStep(page, frames[:], True, frames.index(page), None,
                    f"{page} is already in memory")


def _free_frame_reason(page, slot):
    return f"empty frame available -> load {page} into frame {slot + 1}"


def page_fifo(refs, n_frames):
    """FIFO - replace the page that has been in memory the longest."""
    frames = [None] * n_frames
    queue = deque()                     # frame numbers, oldest page first
    steps = []
    for page in refs:
        if page in frames:                                  # HIT
            steps.append(_hit_step(page, frames))
            continue
        if None in frames:                                  # FAULT, free frame
            slot, victim = frames.index(None), None
            reason = _free_frame_reason(page, slot)
        else:                                               # FAULT, replace oldest
            order = ", ".join(frames[s] for s in queue)
            slot = queue.popleft()
            victim = frames[slot]
            reason = f"replace {victim}: it came in first (load order: {order})"
        frames[slot] = page
        queue.append(slot)
        steps.append(PageStep(page, frames[:], False, slot, victim, reason))
    return steps


def page_lru(refs, n_frames):
    """LRU - replace the page that has not been used for the longest time."""
    frames = [None] * n_frames
    last_used = [-1] * n_frames         # step when each frame was last used
    steps = []
    for t, page in enumerate(refs):
        if page in frames:                                  # HIT
            last_used[frames.index(page)] = t
            steps.append(_hit_step(page, frames))
            continue
        if None in frames:                                  # FAULT, free frame
            slot, victim = frames.index(None), None
            reason = _free_frame_reason(page, slot)
        else:                                               # FAULT, replace LRU page
            slot = min(range(n_frames), key=lambda i: last_used[i])
            victim = frames[slot]
            info = ", ".join(f"{frames[i]} at step {last_used[i] + 1}" for i in range(n_frames))
            reason = f"replace {victim}: least recently used (last used: {info})"
        frames[slot] = page
        last_used[slot] = t
        steps.append(PageStep(page, frames[:], False, slot, victim, reason))
    return steps


def page_optimal(refs, n_frames):
    """OPTIMAL - replace the page that will not be needed for the longest time."""
    frames = [None] * n_frames
    loaded_at = [-1] * n_frames         # only used to break ties (FIFO)
    steps = []
    for t, page in enumerate(refs):
        if page in frames:                                  # HIT
            steps.append(_hit_step(page, frames))
            continue
        if None in frames:                                  # FAULT, free frame
            slot, victim = frames.index(None), None
            reason = _free_frame_reason(page, slot)
        else:                                               # FAULT, look ahead
            def next_use(p):
                for k in range(t + 1, len(refs)):
                    if refs[k] == p:
                        return k
                return INF                                  # never used again

            future = [next_use(p) for p in frames]
            # farthest next use wins; if several pages are never used again,
            # remove the one that was loaded first
            slot = max(range(n_frames), key=lambda i: (future[i], -loaded_at[i]))
            victim = frames[slot]
            info = ", ".join(
                f"{frames[i]} {'never' if future[i] == INF else 'at step ' + str(future[i] + 1)}"
                for i in range(n_frames))
            why = "never used again" if future[slot] == INF else "needed farthest in the future"
            reason = f"replace {victim}: {why} (next use: {info})"
        frames[slot] = page
        loaded_at[slot] = t
        steps.append(PageStep(page, frames[:], False, slot, victim, reason))
    return steps


PAGE_ALGORITHMS = {
    "FIFO": (page_fifo, "First-In, First-Out: replaces the page that has been in "
                        "memory the longest (the one loaded first)."),
    "LRU": (page_lru, "Least Recently Used: replaces the page that has not been "
                      "used for the longest time. It looks at the PAST."),
    "Optimal": (page_optimal, "Optimal (OPT): replaces the page that will not be used "
                              "for the longest time. It looks at the FUTURE and gives "
                              "the fewest faults possible."),
}


@dataclass
class PageResult:
    algorithm: str
    refs: List[str]
    n_frames: int
    steps: List[PageStep]

    @property
    def faults(self) -> int:
        return sum(1 for s in self.steps if not s.hit)

    @property
    def hits(self) -> int:
        return len(self.steps) - self.faults

    @property
    def fault_rate(self) -> float:
        return self.faults / len(self.steps) * 100

    @property
    def hit_rate(self) -> float:
        return self.hits / len(self.steps) * 100


def solve_pages(algorithm, refs, n_frames):
    """Run one page replacement algorithm and return a PageResult."""
    steps = PAGE_ALGORITHMS[algorithm][0](list(refs), n_frames)
    return PageResult(algorithm, list(refs), n_frames, steps)
