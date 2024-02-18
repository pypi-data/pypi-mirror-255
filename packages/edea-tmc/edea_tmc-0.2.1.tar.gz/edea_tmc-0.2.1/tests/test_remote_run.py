import contextlib
import subprocess
import time

import httpx
import numpy as np
import pytest
from httpx import ConnectError

from edea_tmc.remote import MSRunner, AsyncMSRunner
from edea_tmc.sequencer import condition_generator
from tests.mocks import MockStepper, MockValueStepper


@pytest.fixture(autouse=True)
def edea_ms_server():
    p = subprocess.Popen(["python3", "-m", "edea_ms", "--local"])

    # wait for server to be running
    for _ in range(60):
        time.sleep(0.5)
        with contextlib.suppress(TimeoutError, ConnectError):
            r = httpx.get("http://127.0.0.1:8000/")
            if r.status_code != 500:
                break

    r = httpx.get("http://127.0.0.1:8000/api/projects/X5678")
    if r.status_code == 404:
        r = httpx.post("http://127.0.0.1:8000/api/projects",
                       json={"short_code": "X5678", "name": "test_project", "groups": ["group_a", "group_b"], }, )
        assert r.status_code == 200
    yield
    p.terminate()


def test_remote_measurement_run() -> None:
    runner = MSRunner("http://127.0.0.1:8000", "X5678")

    test_parameters = {"Mock_1": [3, 4, 5], "Mock_2": np.concatenate(
        (np.linspace(0.1, 1, 9), np.linspace(0.05, 0.01, 6), (np.logspace(0, 1, 10)),)), "Value_1": ["get_value"], }

    s1 = MockStepper()
    s2 = MockStepper()
    v1 = MockValueStepper(s1, s2)

    steppers = {"Mock_1": s1, "Mock_2": s2, "Value_1": v1}

    steps = condition_generator(test_parameters)

    runner.run(steps, steppers, "TR01", "TEST_DEV", "first test", )

@pytest.mark.asyncio
async def test_async_remote_measurement_run() -> None:
    runner = AsyncMSRunner("http://127.0.0.1:8000", "X5678")

    test_parameters = {"Mock_1": [3, 4, 5], "Mock_2": np.concatenate(
        (np.linspace(0.1, 1, 9), np.linspace(0.05, 0.01, 6), (np.logspace(0, 1, 10)),)), "Value_1": ["get_value"], }

    s1 = MockStepper()
    s2 = MockStepper()
    v1 = MockValueStepper(s1, s2)

    steppers = {"Mock_1": s1, "Mock_2": s2, "Value_1": v1}

    steps = condition_generator(test_parameters)

    await runner.run(steps, steppers, "TR02", "TEST_DEV", "async test", )
