import itertools
from typing import Any

import numpy as np
import pytest
from edea_tmc.measurement_runner import MeasurementRunner  # type: ignore
from edea_tmc.stepper import Stepper, StepResult, StepStatus  # type: ignore
from httpx import AsyncClient


def flexible_test_condition_generator(
    test_parameters: dict[str, list[Any]]
) -> list[dict[str, Any]]:
    """
    General-purpose test condition generator.
    """

    test_conditions = []
    for idx, e in enumerate(itertools.product(*test_parameters.values())):
        d = {"idx": idx}
        for subindex, key in enumerate(test_parameters.keys()):
            d[key] = e[subindex]
        test_conditions.append(d)
    return test_conditions


class CurrentSink(Stepper):
    current_load = 0.0

    def __init__(self) -> None:
        super().__init__([])

    def setup(self) -> None:
        pass

    def step(self, set_point: float) -> StepResult:
        """Set load current in A"""
        self.current_load = set_point

        return StepResult(status=StepStatus.success)

    def measurement_unit(self) -> str:
        return "A"

    def get_current(self) -> float:
        return self.current_load


class VoltageSource(Stepper):
    voltage = 0.0

    def __init__(self) -> None:
        super().__init__([])

    def step(self, set_point: float) -> StepResult:
        self.voltage = set_point

        return StepResult(status=StepStatus.success)

    def measurement_unit(self) -> str:
        return "V"

    def get_voltage(self) -> float:
        return self.voltage


class VirtualDCDC(Stepper):
    """
    A simulated fixed-frequency synchronous buck converter.
    """

    def __init__(self, source: VoltageSource, sink: CurrentSink):
        self.dcr = 0.1  # Ohms
        self.iq = 2.2e-3  # Ampers
        self.set_vout = 5  # Volts

        # dimensionless number for the losses that are linearly
        # dependent on the load
        self.switching_losses_factor = 0.04

        self.source = source
        self.sink = sink

    def get_iin(self, vin: float, iout: float) -> float:
        pout = iout * self.set_vout
        ploss = (
            self.iq * vin + iout**2 * self.dcr
        ) + iout * self.set_vout * self.switching_losses_factor
        pin = pout + ploss
        return pin / vin

    def get_vout(self) -> float:
        return self.set_vout if self.source.get_voltage() > self.set_vout else 0.0

    def step(self, set_point: str | float) -> StepResult:
        if set_point == "i_in":
            return StepResult(
                StepStatus.success,
                self.get_iin(self.source.get_voltage(), self.sink.get_current()),
            )
        else:
            return StepResult(StepStatus.failed, None)


@pytest.mark.asyncio
class TestMeasurementFlow:
    async def test_create_project(self, client: AsyncClient) -> None:
        r = await client.get("/api/projects/X5678")
        if r.status_code == 404:
            r = await client.post(
                "/api/projects",
                json={
                    "short_code": "X5678",
                    "name": "test_project",
                    "groups": ["group_a", "group_b"],
                },
            )
            assert r.status_code == 200

    async def test_measurement_run(self, client: AsyncClient) -> None:
        runner = MeasurementRunner("http://test", "X5678", client=client)

        test_parameters = {
            "Source_V": [3, 4, 5],
            "Sink_I": np.concatenate(
                (
                    np.linspace(0.1, 1, 9),
                    np.linspace(0.05, 0.01, 6),
                    (np.logspace(0, 1, 10)),
                )
            ),
            "DCDC": ["i_in"],
        }

        load = CurrentSink()
        voltage = VoltageSource()

        dcdc = VirtualDCDC(voltage, load)

        test_instruments = {"Source_V": voltage, "Sink_I": load, "DCDC": dcdc}

        conditions = flexible_test_condition_generator(test_parameters)

        await runner.run(
            conditions,
            test_instruments,
            "TR01",
            "TEST_DEV",
            "first test",
        )

    async def test_get_run_results(self, client: AsyncClient) -> None:
        r = await client.get("/api/testruns/measurements/1")
        assert r.status_code == 200
        assert len(r.json()) == 75

    async def test_get_project_runs(self, client: AsyncClient) -> None:
        r = await client.get("/api/testruns/project/X5678")
        assert r.status_code == 200

    async def test_testruns_overview(self, client: AsyncClient) -> None:
        r = await client.get("/api/testruns/overview")
        assert r.status_code == 200

        tr = r.json()
        assert len(tr) > 0
