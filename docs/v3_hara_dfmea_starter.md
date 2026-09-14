# V3 HARA / DFMEA starter (educational)

This is a design-learning artifact, **not a production ISO 26262 safety case or certification claim**.

| Hazard / failure mode | Effect / cause | S/O/D or ASIL placeholder | Mitigation | Requirement / test |
|---|---|---|---|---|
| Command timeout | Loss of fresh brake command | S3 / QM placeholder | 100 ms timeout, zero command | REQ-CAN-008 / TC-CAN-003 |
| Corrupt command | Incorrect brake request | S3 / QM placeholder | checksum + validity, debounced DTC | REQ-CAN-005 / TC-CAN-005 |
| Counter jump | Stale/replayed command | S2 / QM placeholder | sequential alive counter | REQ-CAN-007 / TC-CAN-004 |
| Wheel sensor range | False ABS decision | S2 / QM placeholder | range diagnostic/failsafe | REQ-DIAG-001 / TC-CAN-007 |
| Pressure under-response | Insufficient braking | S3 / QM placeholder | pressure diagnostic/failsafe | REQ-DIAG-002 / TC-V2-011 |
| Stuck high pressure | Unintended braking | S3 / QM placeholder | pressure high DTC | REQ-DIAG-002 / TC-V2-012 |
