from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, Any

from .stepper import Stepper, StepResult, StepStatus

try:
    import polars as pl
except ImportError:
    pl = None  # type: ignore

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore


@dataclass
class SequenceStepResult:
    conditions: dict[str, str | float]
    results: dict[str, str | float]


T = TypeVar("T")
U = TypeVar("U")


class StatefulResult(Generic[T, U]):
    def __init__(self, result: T, state: U) -> None:
        self._result = result
        self._state = state

    @property
    def result(self) -> T:
        return self._result

    @property
    def state(self) -> U:
        return self._state


class MeasurementRunState(Enum):
    NEW = 1
    EXISTING = 2
    IN_PROGRESS = 3
    FAILED = 4
    DONE = 5


class AbstractMeasurementRun(ABC):
    def __init__(self, steps: list[Any], steppers: dict[str, Stepper], ):
        self.steps = steps
        self.sequence_number = 0
        self.steppers = steppers

    def step(self) -> SequenceStepResult:
        if self.sequence_number > len(self.steps):
            raise IndexError("already went through all the steps")

        current_step = self.steps[self.sequence_number]

        step_results: dict[str, str | float] = {}

        for k, v in current_step.items():
            # the conditions contain a sequence number field which is a no-op
            if k == "sequence_number":
                continue

            # technically items within a step should be independent,
            # we could also execute them in parallel here
            res: StepResult | None = self.steppers[k].step(v)

            if res is None:
                continue

            if res.status == StepStatus.SUCCESS:
                if res.value is not None:
                    step_results[k] = res.value
            elif res.status == StepStatus.FAILED:
                raise RunnerError(f"step {self.sequence_number}, {k}:{v} failed")

        self.sequence_number += 1

        return SequenceStepResult(current_step, step_results)

    def polars_df(self) -> "pl.LazyFrame":
        raise NotImplementedError("not implemented")

    def pandas_df(self) -> "pd.DataFrame":
        raise NotImplementedError("not implemented")


class RunnerError(Exception):
    pass
