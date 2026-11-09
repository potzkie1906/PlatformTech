"""Banker's safety check and optional, non-mutating resource request check."""

from dataclasses import dataclass

MAX_PROCESSES = 40
MAX_RESOURCES = 12
MAX_UNITS = 1_000_000

Vector = tuple[int, ...]
Matrix = tuple[Vector, ...]


@dataclass(frozen=True)
class BankState:
    total: Vector
    allocation: Matrix
    maximum: Matrix

    def __post_init__(self):
        if not 1 <= len(self.total) <= MAX_RESOURCES:
            raise ValueError(f"Enter 1-{MAX_RESOURCES} resource types.")
        if not 1 <= len(self.allocation) <= MAX_PROCESSES:
            raise ValueError(f"Enter 1-{MAX_PROCESSES} process rows.")
        if len(self.maximum) != len(self.allocation):
            raise ValueError("Allocation and Max must have the same number of rows.")
        if any(len(row) != len(self.total) for row in (*self.allocation, *self.maximum)):
            raise ValueError("Every Allocation and Max row needs one value per resource type.")
        if any(
            not isinstance(unit, int) or not 0 <= unit <= MAX_UNITS
            for row in (self.total, *self.allocation, *self.maximum)
            for unit in row
        ):
            raise ValueError(f"Resource counts must be whole numbers from 0 to {MAX_UNITS:,}.")
        for index, (allocation, maximum) in enumerate(zip(self.allocation, self.maximum)):
            for column, (allocated, claim, total) in enumerate(zip(allocation, maximum, self.total), 1):
                if allocated > claim:
                    raise ValueError(f"P{index} Allocation exceeds Max in resource column {column}.")
                if claim > total:
                    raise ValueError(f"P{index} Max exceeds Total in resource column {column}.")
        for column, amount in enumerate(self.available, 1):
            if amount < 0:
                raise ValueError(f"Total Allocation exceeds Total in resource column {column}.")

    @property
    def available(self) -> Vector:
        return tuple(
            total - sum(column)
            for total, column in zip(self.total, zip(*self.allocation))
        )

    @property
    def need(self) -> Matrix:
        return tuple(
            tuple(claim - held for claim, held in zip(maximum, allocated))
            for maximum, allocated in zip(self.maximum, self.allocation)
        )


@dataclass(frozen=True)
class WorkCheck:
    process: int
    need: Vector
    before: Vector
    blocking: tuple[int, ...]
    released: Vector | None
    after: Vector
    finish: tuple[bool, ...]


@dataclass(frozen=True)
class SafetyResult:
    initial_work: Vector
    work: Vector
    finish: tuple[bool, ...]
    sequence: tuple[int, ...]
    checks: tuple[WorkCheck, ...]

    @property
    def safe(self) -> bool:
        return all(self.finish)


def exceeding(left: Vector, right: Vector) -> tuple[int, ...]:
    """Resource column indexes where the component-wise <= check fails."""
    return tuple(index for index, (a, b) in enumerate(zip(left, right, strict=True)) if a > b)


def check_safety(state: BankState) -> SafetyResult:
    initial = state.available
    work = initial
    finish = [False] * len(state.allocation)
    sequence = []
    checks = []
    needs = state.need

    while len(sequence) < len(finish):
        # Restart at P0 after each success so equivalent runs give the same trace.
        for index, need in enumerate(needs):
            if finish[index]:
                continue
            before = work
            blocking = exceeding(need, before)
            released = None
            if not blocking:
                released = state.allocation[index]
                work = tuple(free + held for free, held in zip(before, released))
                finish[index] = True
                sequence.append(index)
            checks.append(WorkCheck(index, need, before, blocking, released, work, tuple(finish)))
            if released is not None:
                break
        else:
            break  # One complete scan found no unfinished process that can proceed.
    return SafetyResult(initial, work, tuple(finish), tuple(sequence), tuple(checks))


@dataclass(frozen=True)
class RequestResult:
    process: int
    request: Vector
    need: Vector
    available: Vector
    over_need: tuple[int, ...]
    over_available: tuple[int, ...]
    decision: str
    explanation: str
    tentative: BankState | None = None
    safety: SafetyResult | None = None


def check_request(state: BankState, process: int, request: Vector) -> RequestResult:
    if not 0 <= process < len(state.allocation):
        raise ValueError(f"Requesting process must be P0 through P{len(state.allocation) - 1}.")
    if len(request) != len(state.total) or any(
        not isinstance(value, int) or not 0 <= value <= MAX_UNITS for value in request
    ):
        raise ValueError(f"Request needs one whole number from 0 to {MAX_UNITS:,} per resource type.")

    need, available = state.need[process], state.available
    over_need = exceeding(request, need)
    over_available = exceeding(request, available)
    fields = process, request, need, available, over_need, over_available
    if over_need:
        return RequestResult(*fields, "INVALID REQUEST", "The request exceeds the process's remaining claim.")
    if over_available:
        return RequestResult(*fields, "WAIT", "The requested resources are currently unavailable.")

    allocated = list(state.allocation)
    allocated[process] = tuple(held + asked for held, asked in zip(allocated[process], request))
    tentative = BankState(state.total, tuple(allocated), state.maximum)
    safety = check_safety(tentative)
    if safety.safe:
        return RequestResult(*fields, "GRANT", "The tentative state is safe.", tentative, safety)
    return RequestResult(
        *fields, "WAIT", "The tentative allocation would leave an unsafe state.",
        tentative, safety,
    )
