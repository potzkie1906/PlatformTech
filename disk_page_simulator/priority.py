"""Rank each ready process by its assigned priority."""

from cpu_core import Process, Schedule, schedule_by_rank, summarize

NON_PREEMPTIVE = "Non-preemptive"
PREEMPTIVE = "Preemptive"
LOW_FIRST = "Smaller number first"
HIGH_FIRST = "Larger number first"


def priority_schedule(
    jobs: list[Process], mode: str, priority_order: str, tie_break: str
) -> Schedule:
    direction = 1 if priority_order == LOW_FIRST else -1
    precedence = "Smaller numbers" if direction == 1 else "Larger numbers"
    timeline = schedule_by_rank(
        jobs,
        lambda job, left: direction * job.priority,
        preemptive=mode == PREEMPTIVE,
        tie_break=tie_break,
    )
    return summarize(
        "Priority", jobs, timeline,
        f"{mode} priority. {precedence} have higher priority.",
    )
