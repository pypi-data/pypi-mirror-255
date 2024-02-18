from edea_tmc.stepper import StepResult, StepStatus, Stepper


class MockStepper(Stepper):
    value = 0.0

    def __init__(self) -> None:
        super().__init__()

    def step(self, set_point: float) -> StepResult:
        self.value = set_point
        return StepResult(status=StepStatus.SUCCESS)

    def measurement_unit(self) -> str:
        return "X"


class MockValueStepper(Stepper):

    def __init__(self, s1: Stepper, s2: Stepper):
        super().__init__()
        self.s1 = s1
        self.s2 = s2

    def step(self, set_point: str | float) -> StepResult:
        if set_point == "get_value":
            return StepResult(StepStatus.SUCCESS, "ok", )
        else:
            return StepResult(StepStatus.FAILED, None)


class MockBadStepper(Stepper):
    def __init__(self) -> None:
        super().__init__()

    def step(self, set_point: str) -> StepResult:
        return StepResult(status=StepStatus.FAILED)
