from pathlib import Path
import os
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "sim"))
from brakebench_sil import BrakeBenchSil
from fault_harness import evidence


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
    sil.send(101, 60, (60, 60, 60, 60), 100)
    status = sil.send(101, 60, (60, 60, 60, 60), 140)
    assert (status.state, status.fault, status.pressure_kpa) == ("FAULT", "PRESSURE", 0)
    assert status.dtc == 8 and status.failsafe


def test_invalid_wheel_speed_fault_injection(sil: BrakeBenchSil) -> None:
    sil.send(40, 60, (60, 301, 60, 60), 100)
    status = sil.send(40, 60, (60, 301, 60, 60), 140)
    assert (status.state, status.fault, status.pressure_kpa) == ("FAULT", "WHEEL_SPEED", 0)
    assert status.dtc == 2 and status.failsafe


def test_timeout_reports_dtc_and_failsafe(sil: BrakeBenchSil) -> None:
    sil.send(30, 60, (60, 60, 60, 60), 100)
    status = sil.tick(201)
    assert status.dtc == 1 and status.severity == 2 and status.failsafe
    record = evidence(100, 201, status, "no CAN command frame after 100 ms")
    assert record.latency_ms == 101 and record.dtc == 1 and record.failsafe


def test_wheel_stuck_degrades_without_failsafe(sil: BrakeBenchSil) -> None:
    sil.send(30, 60, (60, 60, 60, 60), 100)
    sil.send(30, 60, (60, 60, 60, 60), 140)
    status = sil.send(30, 60, (60, 60, 60, 60), 180)
    assert status.dtc == 3 and status.severity == 1 and not status.failsafe


def test_non_latched_dtc_recovers_after_stable_input(sil: BrakeBenchSil) -> None:
    sil.send(40, 60, (60, 301, 60, 60), 100)
    sil.send(40, 60, (60, 301, 60, 60), 140)
    status = sil.send(40, 60, (60, 60, 60, 60), 200)
    assert status.dtc == 2
    status = sil.send(40, 60, (61, 61, 61, 61), 300)
    assert status.dtc == 0 and not status.failsafe


def test_corrupt_message_fault_injection(sil: BrakeBenchSil) -> None:
    sil.corrupt(100)
    status = sil.corrupt(140)
    assert status.dtc == 9 and status.failsafe


def test_pressure_under_response_fault_injection(sil: BrakeBenchSil) -> None:
    sil.send(50, 80, (80, 80, 80, 80), 100, feedback_kpa=0)
    status = sil.send(50, 80, (81, 81, 81, 81), 140, feedback_kpa=0)
    assert status.dtc == 5 and status.failsafe


def test_pressure_stuck_high_fault_injection(sil: BrakeBenchSil) -> None:
    sil.send(0, 0, (0, 0, 0, 0), 100, feedback_kpa=2000)
    status = sil.send(0, 0, (1, 1, 1, 1), 140, feedback_kpa=2000)
    assert status.dtc == 6 and status.failsafe


def test_pressure_stuck_low_fault_injection(sil: BrakeBenchSil) -> None:
    sil.send(10, 60, (60, 60, 60, 60), 100, feedback_kpa=0)
    status = sil.send(10, 60, (61, 61, 61, 61), 140, feedback_kpa=0)
    assert status.dtc == 7 and status.failsafe
