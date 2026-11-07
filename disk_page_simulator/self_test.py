"""The '--test' check: runs the algorithms on well-known textbook examples."""

from disk_algorithms import CIRCULAR_ALGORITHMS, solve_disk
from page_algorithms import solve_pages


def run_self_test():
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
    print("All tests passed." if all_ok else "SOME TESTS FAILED.")
    return all_ok
