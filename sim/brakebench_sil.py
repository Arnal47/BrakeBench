"""Small deterministic SIL client for the BrakeBench stdin/stdout ECU runner."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Status:
    state: str
    abs_active: bool
    fault: str
    pressure_kpa: int


class BrakeBenchSil:
    def __init__(self, runner: str | Path) -> None:
        self._process = subprocess.Popen(
            [str(runner)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, bufsize=1,
        )

    def send(self, request: int, vehicle: int, wheels: tuple[int, int, int, int], timestamp_ms: int) -> Status:
        return self._write(f"{request},{vehicle},{wheels[0]},{wheels[1]},{wheels[2]},{wheels[3]},{timestamp_ms}")

    def tick(self, timestamp_ms: int) -> Status:
        return self._write(f"TICK,{timestamp_ms}")

    def close(self) -> None:
        if self._process.stdin:
            self._process.stdin.close()
        self._process.wait(timeout=5)

    def _write(self, line: str) -> Status:
        assert self._process.stdin and self._process.stdout
        self._process.stdin.write(line + "\n")
        self._process.stdin.flush()
        fields = dict(field.split("=", 1) for field in self._process.stdout.readline().strip().split(","))
        return Status(fields["STATE"], fields["ABS"] == "1", fields["FAULT"], int(fields["PRESSURE"]))
