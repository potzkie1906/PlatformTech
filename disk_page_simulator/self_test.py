"""The '--test' check: runs the algorithms on well-known textbook examples."""

from bankers import BankState, check_request, check_safety
from cpu_core import INPUT_ORDER, common_schedules, parse_workload
from priority import LOW_FIRST, NON_PREEMPTIVE, priority_schedule
from round_robin import round_robin
from disk_algorithms import CIRCULAR_ALGORITHMS, solve_disk
from page_algorithms import solve_pages


def _run_disk_page_tests():
    """Check the algorithms against well-known textbook answers."""
    queue, head, last = [98, 183, 37, 122, 14, 124, 65, 67], 53, 199
    disk_cases = [   # (algorithm, direction, count return jump, expected total)
        ("FCFS", "up", True, 640), ("SSTF", "up", True, 236),
        ("SCAN", "down", True, 236), ("SCAN", "up", True, 331),
        ("C-SCAN", "up", True, 382), ("C-SCAN", "up", False, 183),
        ("LOOK", "down", True, 208), ("LOOK", "up", True, 299),
        ("C-LOOK", "up", True, 322), ("C-LOOK", "up", False, 153),
    ]
    refs = "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1".split()
    belady = "1 2 3 4 1 2 5 1 2 3 4 5".split()
    page_cases = [   # (algorithm, reference string, frames, expected faults)
        ("FIFO", refs, 3, 15), ("LRU", refs, 3, 12), ("Optimal", refs, 3, 9),
        ("FIFO", belady, 3, 9), ("FIFO", belady, 4, 10),    # Belady's anomaly
    ]
    all_ok = True
    print("Disk scheduling  (queue 98 183 37 122 14 124 65 67, head 53, 200 cylinders)")
    for algo, direction, count, expected in disk_cases:
        got = solve_disk(algo, queue, head, last, direction, count).total
        ok = got == expected
        all_ok &= ok
        extra = ""
        if algo in CIRCULAR_ALGORITHMS:
            extra = " return counted" if count else " return not counted"
        print(f"  {'OK ' if ok else 'BAD'} {algo:<6} {direction:<4}{extra:<20} {got:>4}"
              f"  (expected {expected})")
    print("Page replacement")
    for algo, ref_string, frames, expected in page_cases:
        got = solve_pages(algo, ref_string, frames).faults
        ok = got == expected
        all_ok &= ok
        print(f"  {'OK ' if ok else 'BAD'} {algo:<7} {frames} frames  {' '.join(ref_string):<40} "
              f"{got:>3} faults  (expected {expected})")
    print("Disk and page checks passed." if all_ok else "Disk or page checks failed.")
    return all_ok


def run_self_test():
    legacy_ok = _run_disk_page_tests()
    jobs = parse_workload("4", "P1 0 7 4\nP2 2 4 1\nP3 4 1 3\nP4 5 4 2", True)
    cpu = common_schedules(jobs, INPUT_ORDER)
    priority = priority_schedule(jobs, NON_PREEMPTIVE, LOW_FIRST, INPUT_ORDER)
    rr = round_robin(jobs, 2)
    bank = BankState((5, 3), ((2, 0), (1, 1), (1, 1)), ((5, 2), (2, 2), (3, 2)))
    unsafe = BankState((3,), ((2,), (1,)), ((3,), (2,)))
    checks = (
        ("FCFS, SJF, SRTF means", [row.averages for row in cpu],
         [(8.75, 4.75, 4.75), (8.0, 4.0, 4.0), (7.0, 3.0, 0.5)]),
        ("Priority means", priority.averages, (9.5, 5.5, 5.5)),
        ("RR means and slices", (rr.averages, len(rr.slices)), ((9.0, 5.0, 1.5), 9)),
        ("Banker's safe sequence", check_safety(bank).sequence, (1, 2, 0)),
        ("Banker's unsafe state", check_safety(unsafe).safe, False),
        ("Banker's grant and wait", (check_request(bank, 1, (1, 1)).decision,
                                     check_request(bank, 0, (1, 0)).decision), ("GRANT", "WAIT")),
    )
    all_ok = legacy_ok
    for label, got, expected in checks:
        ok = got == expected
        print(f"{'OK' if ok else 'BAD'} {label}: {got} (expected {expected})")
        all_ok &= ok
    return all_ok