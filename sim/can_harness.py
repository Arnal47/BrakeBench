"""DBC-driven, in-process CAN SIL harness; no brake decisions live here."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import can
import cantools
from brakebench_sil import BrakeBenchSil, Status


@dataclass(frozen=True)
class CanEvidence:
    test_id: str; requirement_id: str; result: str; injected_at_ms: int | None
    detected_at_ms: int | None; dtc: int; failsafe: bool; recovery: bool; artifact: str


class DbcCanHarness:
    def __init__(self, runner: str | Path, dbc: str | Path) -> None:
        self.db = cantools.database.load_file(str(dbc))
        self.bus = can.Bus(interface="virtual", channel="brakebench-v3", receive_own_messages=True)
        self.sil = BrakeBenchSil(runner); self.values: dict[str, dict[str, Any]] = {}
        self.last_alive: dict[str, int] = {}; self.now = 0

    def close(self) -> None: self.bus.shutdown(); self.sil.close()
    def frame(self, message: str, values: dict[str, Any], *, corrupt=False) -> can.Message:
        spec = self.db.get_message_by_name(message); payload = dict(values)
        payload.setdefault("Checksum", 0); payload["Checksum"] = self._checksum(spec, payload)
        raw = bytearray(spec.encode(payload, strict=False));
        if corrupt: raw[0] ^= 1
        return can.Message(arbitration_id=spec.frame_id, data=raw, is_extended_id=False)
    def deliver(self, frame: can.Message, now_ms: int) -> Status:
        self.now = now_ms; self.bus.send(frame); rx = self.bus.recv(0.1); assert rx is not None
        spec = self.db.get_message_by_frame_id(rx.arbitration_id); decoded = spec.decode(rx.data)
        valid = bool(decoded["Validity"]) and decoded["Checksum"] == self._checksum(spec, decoded)
        alive = int(decoded["AliveCounter"])
        if spec.name in self.last_alive and alive != (self.last_alive[spec.name] + 1) % 16: valid = False
        self.last_alive[spec.name] = alive
        self.values[spec.name] = decoded
        if not valid: return self.sil.corrupt(now_ms)
        required = {"Brake_Command", "Wheel_Speeds", "Brake_Pressure_Feedback"}
        if not required.issubset(self.values):
            return Status("INIT", False, "NONE", 0, 0, 0, False)
        c, w, p = (self.values[n] for n in ("Brake_Command", "Wheel_Speeds", "Brake_Pressure_Feedback"))
        return self.sil.send(int(c["BrakeRequest"]), int(c["VehicleSpeed"]), tuple(int(w[k]) for k in ("WheelSpeedFL","WheelSpeedFR","WheelSpeedRL","WheelSpeedRR")), now_ms, int(p["BrakePressureFeedback"]))
    def tick(self, now_ms: int) -> Status: self.now = now_ms; return self.sil.tick(now_ms)
    def status_frame(self, status: Status, alive: int) -> can.Message:
        return self.frame("Brake_ECU_Status", {"BrakePressureCommand": status.pressure_kpa,
            "ABS_Active": int(status.abs_active), "ECU_State": {"INIT": 0, "IDLE": 1,
            "BRAKING": 2, "ABS_ACTIVE": 3, "FAULT": 4}[status.state], "DTC": status.dtc,
            "Severity": status.severity, "Failsafe": int(status.failsafe), "AliveCounter": alive,
            "Validity": 1})
    @staticmethod
    def _checksum(spec: Any, values: dict[str, Any]) -> int:
        material = sum(int(v) for k, v in values.items() if k != "Checksum") + spec.frame_id
        return material & 0xFF
