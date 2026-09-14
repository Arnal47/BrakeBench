# V3 Validation Test Plan

Tests operate only through the DBC-encoded virtual CAN frames and runner output. `TC-CAN-001..007` cover nominal/status roundtrip, ABS, dropped-frame timeout, alive counter, checksum/validity, delayed/out-of-order traffic, and one wheel out of range. Existing V2 tests cover pressure faults, wheel faults, latching/clear, and recovery.

Run `py -3 tools/generate_validation_report.py --junit build/pytest.xml` after pytest. It reads the real JUnit outcome and writes Markdown, CSV and JSON evidence; it never accepts hand-entered Pass values.
