# V3 Validation Test Plan

Tests operate only through the DBC-encoded virtual CAN frames and runner output. `TC-CAN-001..009` cover nominal/status roundtrip, ABS, dropped-frame timeout, alive counter, independent checksum and Validity=0 checks, delayed/out-of-order traffic, one wheel out of range, and the DBC IDs/cycle/signal metadata contract. Existing V2 tests cover pressure faults, wheel faults, latching/clear, and recovery.

Run pytest with `BRAKEBENCH_EVIDENCE=build/can_evidence.json`, then `py -3 tools/generate_validation_report.py --junit build/pytest.xml --evidence build/can_evidence.json`. The test harness records the observed timestamp, DTC, failsafe/degraded state and recovery flag from the runner; the generator joins that artifact with real JUnit outcomes. It never accepts hand-entered verdict or evidence values.
