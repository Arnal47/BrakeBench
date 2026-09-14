"""Timestamped, public-interface evidence records for SIL fault scenarios."""
from dataclasses import dataclass

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


def evidence(injected_at_ms: int, detected_at_ms: int, status: Status, root_cause_evidence: str) -> FaultEvidence:
    """Build an auditable record from runner output; never infer a DTC in Python."""
    return FaultEvidence(injected_at_ms, detected_at_ms, status.dtc, status.failsafe, root_cause_evidence)
