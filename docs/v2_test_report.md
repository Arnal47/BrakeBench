# BrakeBench V2 verification report

## Results

| Suite | Result | Evidence |
|---|---:|---|
| CTest | 1/1 pass | C11 unit target |
| Python SIL | 13/13 pass | public runner input/output only |

## Covered scenarios

Nominal braking, ABS, CAN timeout, invalid request, wheel range, wheel stuck, wheel mismatch, non-latched recovery, message corruption, pressure under-response, pressure stuck high, and pressure stuck low are exercised with timestamped inputs. The SIL assertions inspect runner status fields including `DTC`, `SEVERITY`, and `FAILSAFE`.

## Diagnostic latency

Except for CAN timeout, persistent conditions require `DIAG_CONFIRM_MS` (40 ms) before confirmation. Non-latched DTCs require `DIAG_RECOVERY_MS` (100 ms) of valid evidence before clearing. The timestamps in the SIL scenarios demonstrate these behaviors.

Root-cause inference is exercised by the timeout SIL scenario using the observed DTC plus timestamped missing-command evidence; the inferred conclusion is asserted in the test.
