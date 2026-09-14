# V2 requirement traceability

| Requirement | Public ECU evidence | Automated test | Result |
|---|---|---|---|
| DTC status is externally observable | `DTC`, `SEVERITY`, `FAILSAFE` runner fields | `test_timeout_reports_dtc_and_failsafe` | Pass |
| CAN timeout enters safe state | zero pressure, timeout DTC, failsafe | `test_can_timeout_fault_injection` | Pass |
| DTC confirmation uses a 40 ms debounce | initial input remains non-faulted; second timestamp confirms | `test_overpressure_fault_injection`, `test_invalid_wheel_speed_fault_injection` | Pass |
| Invalid request is safe | `SIGNAL_INVALID` DTC and zero pressure | `test_overpressure_fault_injection` | Pass |
| Wheel range violation is safe | wheel-range DTC and zero pressure | `test_invalid_wheel_speed_fault_injection` | Pass |
| Four-wheel plausibility mismatch degrades control | mismatch DTC and degraded severity | `test_wheel_mismatch_degrades` | Pass |
| Wheel-stuck fault degrades control | wheel-stuck DTC and degraded severity | `test_wheel_stuck_degrades_without_failsafe` | Pass |
| Corrupt CAN signal is safe | message-corrupt DTC and failsafe | `test_corrupt_message_fault_injection` | Pass |
| Pressure feedback faults are safe | pressure DTC and failsafe | `test_pressure_under_response_fault_injection`, `test_pressure_stuck_high_fault_injection`, `test_pressure_stuck_low_fault_injection` | Pass |
| Non-latched fault recovery is delayed | DTC remains then clears after 100 ms | `test_non_latched_dtc_recovers_after_stable_input` | Pass |

Verification is performed through the runner’s public input/output interface; Python does not duplicate ECU diagnostic logic.
