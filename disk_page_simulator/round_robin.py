"""Round Robin with one trace row per CPU slice."""

from collections import deque

from cpu_core import Process, Schedule, Slice, summarize

MAX_SLICES = 3_000


def round_robin(jobs: list[Process], quantum: int) -> Schedule:
    if quantum < 1:
        raise ValueError("The Round Robin time quantum must be positive.")
    slices_needed = sum((job.burst + quantum - 1) // quantum for job in jobs)
    if slices_needed > MAX_SLICES:
        raise ValueError(
            f"Round Robin would need {slices_needed:,} CPU slices. "
            f"Use a larger quantum for the {MAX_SLICES:,}-slice display limit."
        )

    # Python's stable sort preserves input order for simultaneous arrivals.
    incoming = deque(sorted(jobs, key=lambda job: job.arrival))
    ready = deque()
    remaining = {job.pid: job.burst for job in jobs}
    timeline = []
    time = 0

    def enqueue_arrivals():
        while incoming and incoming[0].arrival <= time:
            ready.append(incoming.popleft())

    while incoming or ready:
        enqueue_arrivals()
        if not ready:
            next_arrival = incoming[0].arrival
            timeline.append(Slice(None, time, next_arrival))
            time = next_arrival
            enqueue_arrivals()

        job = ready.popleft()
        duration = min(quantum, remaining[job.pid])
        remaining[job.pid] -= duration
        timeline.append(Slice(job.pid, time, time + duration, remaining[job.pid]))
        time += duration

        # Arrivals through the end of the slice join before this process requeues.
        enqueue_arrivals()
        if remaining[job.pid]:
            ready.append(job)

    return summarize("Round Robin", jobs, timeline, f"Time quantum = {quantum}.")
