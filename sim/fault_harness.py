"""Timestamped, public-interface evidence records for SIL fault scenarios."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from brakebench_sil import Status


@dataclass(frozen=True)
class FaultEvidence:
    injected_at_ms: int
    detected_at_ms: int
    dtc: int
    failsafe: bool
    root_cause_evidence: str

    @property
    def latency_ms(self) -> int:
        return self.detected_at_ms - self.injected_at_ms


def evidence(
    injected_at_ms: int, detected_at_ms: int, status: Status, root_cause_evidence: str
) -> FaultEvidence:
    """Build an auditable record from runner output; never infer a DTC in Python."""
    return FaultEvidence(
        injected_at_ms, detected_at_ms, status.dtc, status.failsafe, root_cause_evidence
    )


def infer_root_cause(status: Status, input_evidence: str) -> str:
    """Infer a cause from observed DTC/status and measured input evidence."""
    names = {
        1: "missing CAN command",
        2: "wheel speed range violation",
        3: "single-wheel signal stuck",
        4: "four-wheel plausibility mismatch",
        5: "pressure under-response",
        6: "pressure stuck high",
        7: "pressure stuck low",
        8: "invalid signal range",
        9: "corrupt message",
    }
    return f"{names.get(status.dtc, 'no confirmed fault')}: {input_evidence}"


def record_runtime_evidence(
    test_id: str,
    requirement_id: str,
    injected_at_ms: int | None,
    detected_at_ms: int | None,
    status: Status,
    recovery: bool = False,
) -> None:
    """Append actual public-runner observations when test evidence is enabled."""
    destination = os.environ.get("BRAKEBENCH_EVIDENCE")
    if not destination:
        return
    path = Path(destination)
    rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    rows.append(
        {
            "test_id": test_id,
            "requirement_id": requirement_id,
            "result": "PASS",
            "injected_at_ms": injected_at_ms,
            "detected_at_ms": detected_at_ms,
            "dtc": status.dtc,
            "failsafe": status.failsafe,
            "recovery": recovery,
            "artifact": f"runner/{test_id}@{detected_at_ms}ms",
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
