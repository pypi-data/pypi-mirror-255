import asyncio
import io
import platform
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from getpass import getuser
from typing import Any

import httpx

from .runner import StatefulResult, MeasurementRunState, AbstractMeasurementRun, RunnerError
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


class RunnerSetupError(RunnerError):
    pass


class ProjectNotFoundError(RunnerError):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message

    def __str__(self) -> str:
        return self.message


@dataclass
class TestRunModel:
    project_id: int
    short_code: str
    dut_id: str
    machine_hostname: str
    user_name: str
    test_name: str
    id: int | None = None
    data: dict | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    state: str | None = None


class AsyncRemoteMeasurementRun(AbstractMeasurementRun):
    def __init__(self, testrun_id: int, client: httpx.AsyncClient, steps: list[Any], steppers: dict[str, Stepper], ):
        super().__init__(steps, steppers)
        self.testrun_id = testrun_id
        self.client = client

    async def set_state(self, state: str):
        if state == "running":
            action = "start"
        elif state == "failed":
            action = "fail"
        elif state == "complete":
            action = "complete"
        else:
            raise NotImplementedError("unknown state")

        r = await self.client.put(f"/api/testruns/{action}/{self.testrun_id}")
        # TODO: make error information a bit prettier
        if r.status_code != 200:
            raise RunnerError(r.json())

    async def step(self):
        try:
            step_results = super().step()
        except RunnerError as e:
            await self.set_state("failed")
            raise e

        r = await self.client.post("/api/measurement_entries/batch",
                                   json={"sequence_number": self.sequence_number, "testrun_id": self.testrun_id,
                                         "payload": step_results.results, }, )

        # TODO: proper error handling
        if r.status_code != 201:
            raise RunnerError(r.json())

    @property
    def _parquet_url(self) -> str:
        return f"/api/testruns/measurements/{self.testrun_id}?format=parquet"

    def polars_df(self) -> "pl.LazyFrame":
        if pl:
            r = asyncio.run(self.client.get(self._parquet_url))
            return pl.read_parquet(r.content).lazy()
        raise NotImplementedError("optional polars dependency is unavailable")

    def pandas_df(self) -> "pd.DataFrame":
        if pd:
            r = asyncio.run(self.client.get(self._parquet_url))
            return pd.read_parquet(io.BytesIO(r.content))
        raise NotImplementedError("optional pandas dependency is unavailable")


class AsyncMSRunner:
    project_id: int | None = None
    current_step: int | None = None
    testrun_id: int | None = None
    extra_run_data: dict[str, Any] | None = None

    def __init__(self, ms_url: str, project_number: str, extra_run_data: dict[str, Any] | None = None,
                 client: httpx.AsyncClient | None = None, client_headers: dict[str, str] | None = None, ) -> None:
        self.ms_url = ms_url.rstrip("/")
        self.project_number = project_number
        self.extra_run_data = extra_run_data

        self.client = (httpx.AsyncClient(base_url=self.ms_url, headers=client_headers) if client is None else client)

    async def run(self, steps: list[dict], steppers: dict[str, Stepper], short_code: str, dut_id: str,
                  test_name: str, ) -> AsyncRemoteMeasurementRun:
        """run executes the test plan or returns the already existing plan if called
        with the same short_code again.
        """

        # 1. check if the project exists and get the project id
        setup_res = await self.setup_run(steps, steppers, short_code, dut_id, test_name)
        run = setup_res.result

        if setup_res.state != MeasurementRunState.NEW:
            return run

        # 2. set our testrun to the running state
        await run.set_state("running")

        # display a progress bar when running interactively
        if hasattr(sys, "ps1") and tqdm is not None:
            for _ in tqdm(steps, desc=f"SC: {short_code}, DUT: {dut_id}", unit="step"):
                await run.step()
        else:
            for _ in steps:
                await run.step()

        # 4. set the run as completed
        await run.set_state("complete")

        return run

    async def setup_run(self, steps: list[dict], steppers: dict[str, Stepper], short_code: str, dut_id: str,
                        test_name: str, ) -> StatefulResult[AsyncRemoteMeasurementRun, MeasurementRunState]:
        await self._init_project()

        tr = await self._ensure_testrun(short_code, dut_id, test_name)

        if tr.result.id is None:
            raise ValueError("_ensure_testrun didn't return a valid testrun")

        # create a MeasurementRun helper class from the testrun
        mr = AsyncRemoteMeasurementRun(tr.result.id, self.client, steps, steppers)

        # don't continue with the setup if the run already exists
        if tr.state == MeasurementRunState.EXISTING:
            return StatefulResult(mr, tr.state)

        # 2.1. get information form the steppers
        columns: dict[str, dict] = {name: {"data_source": s.data_source(), "description": s.description(),
                                           "measurement_unit": s.measurement_unit(), } for name, s in steppers.items()}

        # 2.2. create all the setup data
        r = await self.client.post(f"/api/testruns/setup/{tr.result.id}", json={"steps": steps, "columns": columns, }, )
        if r.status_code != 200:
            raise RunnerError(f"could not set up run, status: {r.status_code}, response: {r.text}")

        return StatefulResult(mr, tr.state)

    async def _ensure_testrun(self, short_code: str, dut_id: str, test_name: str) -> StatefulResult[
        TestRunModel, MeasurementRunState]:
        """_ensure_testrun checks if this testrun already exists and returns it
        instead of creating a duplicate.

        returns a StatefulResult with the model and the status of the run.
        """
        testrun_id: int | None = None
        mod: TestRunModel | None = None

        # check if this testrun already exists
        r = await self.client.get(f"/api/testruns/{short_code}")
        if r.status_code == 200:
            mod = TestRunModel(**r.json())  # convert from dict to the model
            testrun_id = mod.id

        if self.project_id is None:
            raise ValueError("project not initialized")

        run = TestRunModel(id=testrun_id, project_id=self.project_id, short_code=short_code, dut_id=dut_id,
                           machine_hostname=platform.node(), user_name=getuser(), test_name=test_name,
                           data=self.extra_run_data, )

        # check if parameters changed and err out or return the existing run
        if mod:
            if run == mod:
                return StatefulResult(mod, MeasurementRunState.EXISTING)

            msg = ("testrun with this short code but different params already exists\n"
                   f"remote: {mod}\n"
                   f"local: {run}")
            raise RunnerSetupError(msg)

        # create a new testrun if it doesn't exist yet
        r = await self.client.post("/api/testruns", json=asdict(run))
        if r.status_code != 201:
            raise RunnerSetupError(r.json())

        run.id = r.json()["id"]

        return StatefulResult(run, MeasurementRunState.NEW)

    async def _init_project(self):
        """
        Initialize the project in the edea-ms server
        :return:
        """
        # check if the project id is set and fetch it from the ms otherwise
        if self.project_id is None:
            r = await self.client.get(f"/api/projects/{self.project_number}")
            if r.status_code == 404:
                raise ProjectNotFoundError(f"project {self.project_number} not found in edea-ms")
            elif r.status_code == 403:
                raise Exception("access denied")
            self.project_id = r.json()["id"]


class RemoteMeasurementRun(AbstractMeasurementRun):

    def __init__(self, testrun_id: int, client: httpx.AsyncClient, steps: list[Any], steppers: dict[str, Stepper]):
        super().__init__(steps, steppers)
        self._internal_runner = AsyncRemoteMeasurementRun(testrun_id, client, steps, steppers)

    def set_state(self, state: str):
        return asyncio.run(self._internal_runner.set_state(state))

    def step(self):
        return asyncio.run(self._internal_runner.step())


class MSRunner:

    def __init__(self, ms_url: str, project_number: str, extra_run_data: dict[str, Any] | None = None,
                 client: httpx.AsyncClient | None = None, client_headers: dict[str, str] | None = None, ) -> None:
        self._internal_runner = AsyncMSRunner(ms_url, project_number, extra_run_data, client, client_headers)

    def run(self, steps: list[dict], steppers: dict[str, Stepper], short_code: str, dut_id: str,
            test_name: str, ) -> RemoteMeasurementRun:
        ar = asyncio.run(self._internal_runner.run(steps, steppers, short_code, dut_id, test_name))
        return RemoteMeasurementRun(ar.testrun_id, ar.client, ar.steps, ar.steppers)

    def setup_run(self, steps: list[dict], steppers: dict[str, Stepper], short_code: str, dut_id: str,
                  test_name: str, ) -> StatefulResult[RemoteMeasurementRun, MeasurementRunState]:
        tr = asyncio.run(self._internal_runner.setup_run(steps, steppers, short_code, dut_id, test_name))
        mr = RemoteMeasurementRun(tr.result.testrun_id, self._internal_runner.client, steps, steppers)

        return StatefulResult(mr, tr.state)
