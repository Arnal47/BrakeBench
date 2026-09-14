import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "sim"))
from can_harness import DbcCanHarness

DBC = Path(__file__).parents[2] / "dbc" / "brakebench_v3.dbc"


@pytest.fixture
def can_sil():
    runner = os.environ.get("BRAKEBENCH_RUNNER")
    if not runner:
        pytest.skip("BRAKEBENCH_RUNNER is not set")
    h = DbcCanHarness(runner, DBC)
    yield h
    evidence_path = os.environ.get("BRAKEBENCH_EVIDENCE")
    if evidence_path:
        h.append_evidence(evidence_path)
    h.close()


def send_set(
    h, now, alive, request=50, vehicle=80, wheels=(80, 80, 80, 80), pressure=6000
):
    h.deliver(
        h.frame(
            "Brake_Command",
            {
                "BrakeRequest": request,
                "VehicleSpeed": vehicle,
                "AliveCounter": alive,
                "Validity": 1,
            },
        ),
        now,
    )
    h.deliver(
        h.frame(
            "Wheel_Speeds",
            dict(
                zip(
                    ("WheelSpeedFL", "WheelSpeedFR", "WheelSpeedRL", "WheelSpeedRR"),
                    wheels,
                )
            )
            | {"AliveCounter": alive, "Validity": 1},
        ),
        now,
    )
    return h.deliver(
        h.frame(
            "Brake_Pressure_Feedback",
            {"BrakePressureFeedback": pressure, "AliveCounter": alive, "Validity": 1},
        ),
        now,
    )


def test_dbc_nominal_and_status_roundtrip(can_sil):
    status = send_set(can_sil, 100, 0)
    assert status.pressure_kpa == 6000 and status.state == "BRAKING"
    frame = can_sil.status_frame(status, 0)
    assert (
        can_sil.db.decode_message(frame.arbitration_id, frame.data)[
            "BrakePressureCommand"
        ]
        == 6000
    )
    can_sil.capture_evidence(
        "TC-CAN-001",
        "REQ-CAN-001;REQ-CAN-002;REQ-CAN-003;REQ-CAN-004;REQ-CTRL-001",
        None,
        status,
    )


def test_dbc_abs(can_sil):
    status = send_set(can_sil, 100, 0, wheels=(80, 50, 80, 80))
    assert status.abs_active
    can_sil.capture_evidence("TC-CAN-002", "REQ-CTRL-002", 100, status)


def test_message_timeout_via_dropped_frames(can_sil):
    send_set(can_sil, 100, 0)
    status = can_sil.tick(201)
    assert status.dtc == 1 and status.failsafe
    can_sil.capture_evidence("TC-CAN-003", "REQ-CAN-008;REQ-SAFE-001", 100, status)


def test_alive_counter_error_is_detected(can_sil):
    send_set(can_sil, 100, 0)
    can_sil.deliver(
        can_sil.frame(
            "Brake_Command",
            {"BrakeRequest": 50, "VehicleSpeed": 80, "AliveCounter": 4, "Validity": 1},
        ),
        120,
    )
    can_sil.deliver(
        can_sil.frame(
            "Brake_Command",
            {"BrakeRequest": 50, "VehicleSpeed": 80, "AliveCounter": 4, "Validity": 1},
        ),
        140,
    )
    status = can_sil.deliver(
        can_sil.frame(
            "Brake_Command",
            {"BrakeRequest": 50, "VehicleSpeed": 80, "AliveCounter": 4, "Validity": 1},
        ),
        160,
    )
    assert status.dtc == 9 and status.failsafe
    can_sil.capture_evidence("TC-CAN-004", "REQ-CAN-007", 120, status)


def test_checksum_error_is_detected(can_sil):
    bad = can_sil.frame(
        "Brake_Command",
        {"BrakeRequest": 50, "VehicleSpeed": 80, "AliveCounter": 0, "Validity": 1},
        corrupt=True,
    )
    can_sil.deliver(bad, 100)
    status = can_sil.deliver(bad, 140)
    assert status.dtc == 9 and status.failsafe
    can_sil.capture_evidence("TC-CAN-005", "REQ-CAN-005", 100, status)


def test_validity_zero_is_detected_independently(can_sil):
    invalid = can_sil.frame(
        "Brake_Command",
        {"BrakeRequest": 50, "VehicleSpeed": 80, "AliveCounter": 0, "Validity": 0},
    )
    can_sil.deliver(invalid, 100)
    status = can_sil.deliver(invalid, 140)
    assert status.dtc == 9 and status.failsafe
    can_sil.capture_evidence("TC-CAN-006", "REQ-CAN-006", 100, status)


def test_out_of_order_and_delayed_frame_are_public_faults(can_sil):
    send_set(can_sil, 100, 0)
    send_set(can_sil, 140, 1)
    status = can_sil.deliver(
        can_sil.frame(
            "Wheel_Speeds",
            {
                "WheelSpeedFL": 80,
                "WheelSpeedFR": 80,
                "WheelSpeedRL": 80,
                "WheelSpeedRR": 80,
                "AliveCounter": 0,
                "Validity": 1,
            },
        ),
        160,
    )
    status = can_sil.deliver(
        can_sil.frame(
            "Wheel_Speeds",
            {
                "WheelSpeedFL": 80,
                "WheelSpeedFR": 80,
                "WheelSpeedRL": 80,
                "WheelSpeedRR": 80,
                "AliveCounter": 0,
                "Validity": 1,
            },
        ),
        180,
    )
    assert status.dtc == 9
    can_sil.capture_evidence("TC-CAN-007", "REQ-CAN-009", 160, status)


def test_single_signal_out_of_range_reaches_ecu(can_sil):
    send_set(can_sil, 100, 0, wheels=(80, 301, 80, 80))
    status = send_set(can_sil, 140, 1, wheels=(80, 301, 80, 80))
    assert status.dtc == 2 and status.failsafe
    can_sil.capture_evidence("TC-CAN-008", "REQ-DIAG-001", 100, status)


def test_dbc_contract_ids_cycles_and_signal_metadata(can_sil):
    status = send_set(can_sil, 100, 0)
    expected = {
        "Brake_Command": (
            0x180,
            {"BrakeRequest": ("%", 1, 0, 100), "VehicleSpeed": ("kph", 0.5, 0, 250)},
        ),
        "Wheel_Speeds": (0x181, {"WheelSpeedFL": ("kph", 0.5, 0, 300)}),
        "Brake_Pressure_Feedback": (
            0x182,
            {"BrakePressureFeedback": ("kPa", 1, 0, 12000)},
        ),
        "Brake_ECU_Status": (0x280, {"BrakePressureCommand": ("kPa", 1, 0, 12000)}),
    }
    for name, (identifier, signals) in expected.items():
        message = can_sil.db.get_message_by_name(name)
        assert message.frame_id == identifier and message.cycle_time == 20
        for signal, metadata in signals.items():
            item = message.get_signal_by_name(signal)
            assert (item.unit, item.scale, item.minimum, item.maximum) == metadata
    can_sil.capture_evidence(
        "TC-CAN-009",
        "REQ-CAN-001;REQ-CAN-002;REQ-CAN-003;REQ-CAN-004",
        None,
        status,
    )
