"""Data, FCFS/SJF/SRTF, and metrics for a single CPU."""

from dataclasses import dataclass
from typing import Callable

MAX_JOBS = 60
MAX_TIME = 1_000_000
INPUT_ORDER = "Input order"
PROCESS_ID = "Process ID"


@dataclass(frozen=True)
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0


@dataclass(frozen=True)
class Slice:
    pid: str | None   # None marks CPU idle time.
    start: int
    end: int
    remaining: int | None = None


@dataclass(frozen=True)
class Metrics:
    process: Process
    completion: int
    turnaround: int
    waiting: int
    response: int


@dataclass(frozen=True)
class Schedule:
    name: str
    slices: list[Slice]
    metrics: list[Metrics]
    detail: str

    @property
    def averages(self) -> tuple[float, float, float]:
        count = len(self.metrics)
        return (
            sum(row.turnaround for row in self.metrics) / count,
            sum(row.waiting for row in self.metrics) / count,
            sum(row.response for row in self.metrics) / count,
        )


def whole(value: str, label: str, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{label} must be a whole number.") from None
    if not minimum <= number <= maximum:
        raise ValueError(f"{label} must be between {minimum:,} and {maximum:,}.")
    return number


def parse_workload(count_text: str, text: str, with_priority: bool) -> list[Process]:
    count = whole(count_text, "Process count", 1, MAX_JOBS)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != count:
        raise ValueError(f"Process count is {count}, but there are {len(lines)} process rows.")

    jobs = []
    seen = set()
    expected = "ID, AT, BT, priority" if with_priority else "ID, AT, BT"
    for row, line in enumerate(lines, start=1):
        cells = [cell.strip() for cell in line.split(",")] if "," in line else line.split()
        if len(cells) != (4 if with_priority else 3):
            raise ValueError(f"Row {row} must have {expected}.")
        pid = cells[0]
        if (not pid or len(pid) > 24 or not pid.isprintable()
                or any(character.isspace() for character in pid) or pid.casefold() == "idle"):
            raise ValueError(f"Row {row} needs an ID of 1-24 characters without spaces. Idle is reserved.")
        if pid in seen:
            raise ValueError(f"Duplicate process ID {pid!r} on row {row}.")
        arrival = whole(cells[1], f"{pid} arrival time", 0, MAX_TIME)
        burst = whole(cells[2], f"{pid} burst time", 1, MAX_TIME)
        priority = whole(cells[3], f"{pid} priority", -MAX_TIME, MAX_TIME) if with_priority else 0
        jobs.append(Process(pid, arrival, burst, priority))
        seen.add(pid)
    return jobs


def schedule_by_rank(
    jobs: list[Process],
    rank: Callable[[Process, int], int],
    *,
    preemptive: bool,
    tie_break: str,
) -> list[Slice]:
    """Run a ranked policy, deciding at arrivals or completions."""
    time = 0
    pending = list(jobs)
    left = {job.pid: job.burst for job in jobs}
    tie_keys = {
        job.pid: job.pid if tie_break == PROCESS_ID else index
        for index, job in enumerate(jobs)
    }
    active = None
    timeline = []

    def rank_of(job):
        return rank(job, left[job.pid])

    while pending:
        ready = [job for job in pending if job.arrival <= time]
        if not ready:
            next_arrival = min(job.arrival for job in pending)
            timeline.append(Slice(None, time, next_arrival))
            time = next_arrival
            continue

        chosen = min(ready, key=lambda job: (rank_of(job), job.arrival, tie_keys[job.pid]))
        # The running process keeps the CPU when a new arrival ties its rank.
        if active is not None and rank_of(active) == rank_of(chosen):
            chosen = active

        end = time + left[chosen.pid]
        if preemptive:
            end = min((job.arrival for job in pending if time < job.arrival < end), default=end)
        left[chosen.pid] -= end - time

        # Adjacent parts of an uninterrupted run form one Gantt block.
        if timeline and timeline[-1].pid == chosen.pid:
            time = timeline.pop().start
        timeline.append(Slice(chosen.pid, time, end, left[chosen.pid]))
        time = end

        active = chosen
        if left[chosen.pid] == 0:
            pending.remove(chosen)
            active = None
    return timeline


def summarize(name: str, jobs: list[Process], timeline: list[Slice], detail: str) -> Schedule:
    first = {}
    completion = {}
    for segment in timeline:
        if segment.pid is not None:
            first.setdefault(segment.pid, segment.start)
            completion[segment.pid] = segment.end

    rows = []
    for job in jobs:
        ct = completion[job.pid]
        tat = ct - job.arrival
        rows.append(Metrics(job, ct, tat, tat - job.burst, first[job.pid] - job.arrival))
    return Schedule(name, timeline, rows, detail)


def common_schedules(jobs: list[Process], tie_break: str) -> list[Schedule]:
    policies = (
        ("FCFS", lambda job, left: job.arrival, False, "First come, first served by arrival time."),
        ("SJF", lambda job, left: job.burst, False, "Non-preemptive shortest job first."),
        ("SRTF", lambda job, left: left, True, "Preemptive shortest remaining time first."),
    )
    return [
        summarize(
            name, jobs,
            schedule_by_rank(jobs, rank, preemptive=preemptive, tie_break=tie_break),
            detail,
        )
        for name, rank, preemptive, detail in policies
    ]
