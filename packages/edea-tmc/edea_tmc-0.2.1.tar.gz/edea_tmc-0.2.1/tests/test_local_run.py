import os.path

import numpy as np
import pytest

from edea_tmc.local import LocalRunner, LocalMeasurementRun
from edea_tmc.runner import RunnerError
from edea_tmc.sequencer import condition_generator
from tests.mocks import MockStepper, MockValueStepper, MockBadStepper

# Test IDs for parametrization
HAPPY_PATH_ID = "happy"
EDGE_CASE_ID = "edge"
ERROR_CASE_ID = "error"

# Test data for parametrization
test_data = [(HAPPY_PATH_ID, "test", False), (EDGE_CASE_ID, "test_convert.ndjson", True), ]


@pytest.mark.parametrize("test_id, filename, convert", test_data)
def test_local_measurement_run_step(test_id, filename, convert):
    # Arrange
    test_parameters = {"Mock_1": [3, 4, 5], "Mock_2": np.concatenate(
        (np.linspace(0.1, 1, 9), np.linspace(0.05, 0.01, 6), (np.logspace(0, 1, 10)),)), "Value_1": ["get_value"], }

    s1 = MockStepper()
    s2 = MockStepper()
    v1 = MockValueStepper(s1, s2)

    steppers = {"Mock_1": s1, "Mock_2": s2, "Value_1": v1}

    steps = condition_generator(test_parameters)

    runner = LocalRunner()
    measurement_run = runner.run(steps, steppers, filename, convert)

    # Assert
    assert os.path.isfile(f"{filename.removesuffix('.ndjson')}.ndjson")
    os.remove(f"{filename.removesuffix('.ndjson')}.ndjson")

    if test_id == HAPPY_PATH_ID:
        assert measurement_run.sequence_number == len(steps)
    elif test_id == EDGE_CASE_ID:
        assert os.path.isfile(f"{filename.removesuffix('.ndjson')}.parquet")
        os.remove(f"{filename.removesuffix('.ndjson')}.parquet")


def test_local_measurement_run_step_fail():
    test_parameters = {"Mock_1": ["get_value"], }
    s1 = MockBadStepper()
    steppers = {"Mock_1": s1}
    steps = condition_generator(test_parameters)

    measurement_run = LocalMeasurementRun(steps, steppers, "test")
    with pytest.raises(RunnerError):
        measurement_run.step()
