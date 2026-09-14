# BrakeBench V2 DTC fault matrix

| DTC | Trigger evidence | Confirmation | Severity | Recovery |
|---|---|---:|---|---|
| CAN_TIMEOUT | No input for more than 100 ms | Immediate | Failsafe, latched | Service reset |
| WHEEL_RANGE | Any wheel speed exceeds 300 kph | 40 ms | Failsafe | Valid input for 100 ms |
| WHEEL_STUCK | Wheel signal remains unchanged while moving | 40 ms | Degraded | Valid changing signal for 100 ms |
| WHEEL_MISMATCH | Mean wheel speed below half vehicle speed | 40 ms | Degraded | Plausible values for 100 ms |
| PRESSURE_UNDER_RESPONSE | Feedback is 1,500 kPa below commanded pressure | 40 ms | Failsafe | Feedback recovers for 100 ms |
| PRESSURE_STUCK_HIGH | Feedback remains above 1,000 kPa at zero command | 40 ms | Failsafe, latched | Service reset |
| PRESSURE_STUCK_LOW | Feedback remains below 100 kPa at a command above 1,000 kPa | 40 ms | Failsafe | Feedback recovers for 100 ms |
| SIGNAL_INVALID | Brake request exceeds valid range | 40 ms | Failsafe | Valid input for 100 ms |
| MESSAGE_CORRUPT | CAN signal-valid flag is false | 40 ms | Failsafe | Valid input for 100 ms |

All thresholds are defined in `include/brake_ecu.h` and `include/diagnostics.h`; the SIL suite interacts only through runner input/output.
