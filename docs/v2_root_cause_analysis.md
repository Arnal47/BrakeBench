# V2 root cause analysis

The SIL harness records timestamped ECU status (`DTC`, `SEVERITY`, `FAILSAFE`) after each injected input. Root-cause conclusions are made from those observable facts, not test names:

- `CAN_TIMEOUT` follows a period with no command frame.
- Wheel DTCs follow out-of-range or cross-wheel plausibility evidence.
- Pressure DTCs compare command-derived pressure to the reported feedback.
- `MESSAGE_CORRUPT` follows an invalid CAN signal flag.

For every scenario, report injection timestamp, confirmation timestamp, latency, DTC, safety response, recovery result, and the input evidence that supports the conclusion.
