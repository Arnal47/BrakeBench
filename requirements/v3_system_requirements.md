# V3 verifiable system requirements

Each row is assessed by `tools/generate_validation_report.py` from pytest results; this is an engineering exercise, not a production safety case.

| ID | Rationale / acceptance criteria | Linked test |
|---|---|---|
| REQ-CAN-001 | Brake command uses DBC ID 0x180, 20 ms and declared scaling. | TC-CAN-009 |
| REQ-CAN-002 | Wheel speeds use DBC ID 0x181, 20 ms and declared scaling. | TC-CAN-009 |
| REQ-CAN-003 | Pressure feedback uses DBC ID 0x182, 20 ms. | TC-CAN-009 |
| REQ-CAN-004 | Status uses DBC ID 0x280 with command, ABS, state, DTC, severity and failsafe. | TC-CAN-009 |
| REQ-CAN-005 | Invalid checksum is confirmed as corrupt-message DTC. | TC-CAN-005 |
| REQ-CAN-006 | Invalid validity bit is confirmed as corrupt-message DTC. | TC-CAN-006 |
| REQ-CAN-007 | Non-sequential alive counter is rejected. | TC-CAN-004 |
| REQ-CAN-008 | Missing command beyond 100 ms enters failsafe. | TC-CAN-003 |
| REQ-CAN-009 | Delayed/out-of-order sequence is rejected. | TC-CAN-007 |
| REQ-CTRL-001 | Nominal 50% request commands 6000 kPa. | TC-CAN-001 |
| REQ-CTRL-002 | ABS reduces command when wheel slip is detected. | TC-CAN-002 |
| REQ-DIAG-001 | Out-of-range individual wheel is debounced to wheel DTC. | TC-CAN-008 |
| REQ-DIAG-002 | Pressure under-response is diagnosed. | TC-V2-011 |
| REQ-DIAG-003 | Latched DTC clear uses ECU public API. | TC-V2-C-001 |
| REQ-SAFE-001 | Confirmed corrupt / timeout faults command failsafe. | TC-CAN-003, TC-CAN-005 |
| REQ-SAFE-002 | Stable input recovers non-latched diagnostic state. | TC-V2-009 |
