from pathlib import Path
import os, sys
import pytest
sys.path.insert(0, str(Path(__file__).parents[2] / "sim"))
from can_harness import DbcCanHarness

DBC = Path(__file__).parents[2] / "dbc" / "brakebench_v3.dbc"

@pytest.fixture
def can_sil():
    runner = os.environ.get("BRAKEBENCH_RUNNER")
    if not runner: pytest.skip("BRAKEBENCH_RUNNER is not set")
    h = DbcCanHarness(runner, DBC); yield h; h.close()

def send_set(h, now, alive, request=50, vehicle=80, wheels=(80,80,80,80), pressure=6000):
    h.deliver(h.frame("Brake_Command", {"BrakeRequest":request,"VehicleSpeed":vehicle,"AliveCounter":alive,"Validity":1}), now)
    h.deliver(h.frame("Wheel_Speeds", dict(zip(("WheelSpeedFL","WheelSpeedFR","WheelSpeedRL","WheelSpeedRR"),wheels)) | {"AliveCounter":alive,"Validity":1}), now)
    return h.deliver(h.frame("Brake_Pressure_Feedback", {"BrakePressureFeedback":pressure,"AliveCounter":alive,"Validity":1}), now)

def test_dbc_nominal_and_status_roundtrip(can_sil):
    status = send_set(can_sil, 100, 0)
    assert status.pressure_kpa == 6000 and status.state == "BRAKING"
    frame = can_sil.status_frame(status, 0)
    assert can_sil.db.decode_message(frame.arbitration_id, frame.data)["BrakePressureCommand"] == 6000

def test_dbc_abs(can_sil):
    assert send_set(can_sil, 100, 0, wheels=(80,50,80,80)).abs_active

def test_message_timeout_via_dropped_frames(can_sil):
    send_set(can_sil, 100, 0)
    status = can_sil.tick(201)
    assert status.dtc == 1 and status.failsafe

def test_alive_counter_error_is_detected(can_sil):
    send_set(can_sil, 100, 0); can_sil.deliver(can_sil.frame("Brake_Command", {"BrakeRequest":50,"VehicleSpeed":80,"AliveCounter":4,"Validity":1}), 120)
    can_sil.deliver(can_sil.frame("Brake_Command", {"BrakeRequest":50,"VehicleSpeed":80,"AliveCounter":4,"Validity":1}), 140)
    status = can_sil.deliver(can_sil.frame("Brake_Command", {"BrakeRequest":50,"VehicleSpeed":80,"AliveCounter":4,"Validity":1}), 160)
    assert status.dtc == 9 and status.failsafe

def test_checksum_and_validity_errors_are_detected(can_sil):
    bad = can_sil.frame("Brake_Command", {"BrakeRequest":50,"VehicleSpeed":80,"AliveCounter":0,"Validity":1}, corrupt=True)
    can_sil.deliver(bad, 100); status = can_sil.deliver(bad, 140)
    assert status.dtc == 9 and status.failsafe

def test_out_of_order_and_delayed_frame_are_public_faults(can_sil):
    send_set(can_sil, 100, 0); send_set(can_sil, 140, 1)
    status = can_sil.deliver(can_sil.frame("Wheel_Speeds", {"WheelSpeedFL":80,"WheelSpeedFR":80,"WheelSpeedRL":80,"WheelSpeedRR":80,"AliveCounter":0,"Validity":1}), 160)
    status = can_sil.deliver(can_sil.frame("Wheel_Speeds", {"WheelSpeedFL":80,"WheelSpeedFR":80,"WheelSpeedRL":80,"WheelSpeedRR":80,"AliveCounter":0,"Validity":1}), 180)
    assert status.dtc == 9

def test_single_signal_out_of_range_reaches_ecu(can_sil):
    send_set(can_sil, 100, 0, wheels=(80,301,80,80)); status = send_set(can_sil, 140, 1, wheels=(80,301,80,80))
    assert status.dtc == 2 and status.failsafe
