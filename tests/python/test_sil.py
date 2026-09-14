from pathlib import Path
import os
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "sim"))
from brakebench_sil import BrakeBenchSil


@pytest.fixture
def sil() -> BrakeBenchSil:
    runner = os.environ.get("BRAKEBENCH_RUNNER")
    if not runner:
        pytest.skip("BRAKEBENCH_RUNNER is not set")
    client = BrakeBenchSil(runner)
    yield client
    client.close()


def test_nominal_braking(sil: BrakeBenchSil) -> None:
    status = sil.send(50, 80, (80, 80, 80, 80), 100)
    assert (status.state, status.fault, status.pressure_kpa) == ("BRAKING", "NONE", 6000)


def test_abs_intervention(sil: BrakeBenchSil) -> None:
    status = sil.send(50, 80, (80, 50, 80, 80), 100)
    assert status.state == "ABS_ACTIVE"
    assert status.abs_active and status.pressure_kpa == 4200


def test_can_timeout_fault_injection(sil: BrakeBenchSil) -> None:
    sil.send(30, 60, (60, 60, 60, 60), 100)
    status = sil.tick(201)
    assert (status.state, status.fault, status.pressure_kpa) == ("FAULT", "CAN_TIMEOUT", 0)


def test_overpressure_fault_injection(sil: BrakeBenchSil) -> None:
    status = sil.send(101, 60, (60, 60, 60, 60), 100)
    assert (status.state, status.fault, status.pressure_kpa) == ("FAULT", "PRESSURE", 0)


def test_invalid_wheel_speed_fault_injection(sil: BrakeBenchSil) -> None:
    status = sil.send(40, 60, (60, 301, 60, 60), 100)
    assert (status.state, status.fault, status.pressure_kpa) == ("FAULT", "WHEEL_SPEED", 0)
