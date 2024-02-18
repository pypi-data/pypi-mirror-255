import json
import sys
from typing import Any

from .runner import AbstractMeasurementRun
from .stepper import Stepper

try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = None  # type: ignore

try:
    import polars as pl
except ImportError:
    pl = None  # type: ignore

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore


class LocalMeasurementRun(AbstractMeasurementRun):
    def __init__(self, steps: list[Any], steppers: dict[str, Stepper], filename: str, convert: bool = False):
        super().__init__(steps, steppers)
        self._file = None
        self.filename = filename.removesuffix(".ndjson") if filename.endswith(".ndjson") else filename
        self._num_steps = len(steps)
        self._convert = convert

    def step(self):
        if self._file is None:
            self._file = open(f"{self.filename}.ndjson", "w")

        res = super().step()
        # merge the results into conditions for a unified view
        line = res.conditions | res.results

        # write to an NDJSON file
        self._file.write(json.dumps(line))
        if self.sequence_number == self._num_steps:
            self._file.close()
            if self._convert:
                if not pl:
                    raise NotImplementedError("polars dependency is unavailable")
                df = pl.read_ndjson(f"{self.filename}.ndjson")
                df.write_parquet(f"{self.filename}.parquet")
        else:
            self._file.write("\n")

    def polars_df(self) -> "pl.LazyFrame":
        if pl:
            if self._convert:
                return pl.scan_parquet(f"{self.filename}.parquet")
            else:
                return pl.scan_ndjson(f"{self.filename}.ndjson")
        raise NotImplementedError("optional polars dependency is unavailable")

    def pandas_df(self) -> "pd.DataFrame":
        if pd:
            return pd.DataFrame(self.filename)
        raise NotImplementedError("optional pandas dependency is unavailable")


class LocalRunner:

    def __init__(self) -> None:
        pass

    def run(self, steps: list[dict], steppers: dict[str, Stepper], filename: str,
            convert: bool = False) -> LocalMeasurementRun:
        """run executes the test plan or returns the already existing plan if called
        with the same short_code again.
        """

        # 1. check if the project exists and get the project id
        run = LocalMeasurementRun(steps, steppers, filename, convert)

        # display a progress bar when running interactively
        if hasattr(sys, "ps1") and tqdm is not None:
            for _ in tqdm(steps, unit="step"):
                run.step()
        else:
            # or simply run without a progress bar
            for _ in steps:
                run.step()

        return run
