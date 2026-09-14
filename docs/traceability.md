# V1 requirements traceability

| ID | Requirement | Implementation | Verification |
|---|---|---|---|
| BRK-001 | Convert a 0–100% brake request to 0–12,000 kPa. | `brake_controller_pressure` | C test and `test_nominal_braking` |
| BRK-002 | Detect wheel slip below 80% of vehicle speed when braking above 10 kph. | `brake_controller_abs_needed` | C test and `test_abs_intervention` |
| BRK-003 | Reduce commanded pressure by 30% during ABS intervention. | `brake_controller_pressure` | C test and `test_abs_intervention` |
| BRK-004 | Enter a safe zero-pressure fault state after 100 ms without CAN input. | `diagnostics_validate` | C test and `test_can_timeout_fault_injection` |
| BRK-005 | Reject implausible wheel speeds and invalid brake pressure requests. | `diagnostics_validate` | `test_invalid_wheel_speed_fault_injection`, `test_overpressure_fault_injection` |
| BRK-006 | Describe request/status CAN payloads. | `dbc/brakebench_v1.dbc` | Manual DBC review |
