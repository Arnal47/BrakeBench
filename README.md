# BrakeBench V1

BrakeBench is a small C11 brake ECU reference implementation with a deterministic stdin/stdout runner and Python software-in-the-loop (SIL) tests. It is an engineering exercise, not production vehicle software.

## Behavior

- Converts brake request percentage into hydraulic pressure up to 12,000 kPa.
- Activates ABS when a wheel is below 80% of vehicle speed while braking at speed.
- Reduces pressure by 30% under ABS.
- Fails safe to zero pressure for stale CAN input, invalid brake request, or implausible wheel speed.

## Build and test

```powershell
cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=clang
cmake --build build
ctest --test-dir build --output-on-failure
$env:BRAKEBENCH_RUNNER = (Resolve-Path build/brake_ecu_runner.exe)
python -m pytest tests/python -q
```

The runner accepts a CSV input frame: `request,vehicle,wheelFL,wheelFR,wheelRL,wheelRR,timestamp_ms`. Send `TICK,timestamp_ms` to advance time without new CAN input. It emits `STATE`, `ABS`, `FAULT`, and `PRESSURE` fields per line.

## Artifacts

- `dbc/brakebench_v1.dbc`: CAN request and status contract.
- `sim/brakebench_sil.py`: lightweight subprocess SIL client.
- `docs/traceability.md`: requirement-to-test mapping.
- `docs/test_report.md`: verification scope and acceptance record.

## V2 diagnostics

V2 adds a debounced diagnostic state machine. The runner status now exposes `DTC`, `SEVERITY`, and `FAILSAFE` in addition to the legacy state, fault, ABS, and pressure fields. A confirmed failsafe DTC commands zero pressure; a degraded DTC preserves controlled operation.

See [the DTC fault matrix](docs/v2_fault_matrix.md) for detection evidence, confirmation timing, severity, latching, and recovery rules, and [root-cause analysis](docs/v2_root_cause_analysis.md) for the evidence-based SIL reporting method.

`sim/fault_harness.py` turns public runner status into timestamped fault evidence without duplicating C diagnostic logic.
