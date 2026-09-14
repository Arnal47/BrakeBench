# BrakeBench V1 verification report

## Scope

Verification covers C11 unit behavior and the process-boundary Python SIL tests. Fault injection includes CAN timeout, excessive request, and implausible wheel speed.

## Acceptance results

| Check | Expected result | Result |
|---|---|---|
| CMake/Ninja clean build | C11 target and runner compile with warnings treated as errors | Pass |
| CTest | ECU nominal, ABS, timeout, and invalid-request unit checks | Pass: 1/1 |
| pytest SIL | Nominal, ABS, CAN-timeout, pressure, and wheel-speed scenarios | Pass: 5/5 |

Final verification was run on 2026-09-14 with Clang 22.1.8, Ninja, Visual Studio Build Tools 2022, and Python 3.14.4. `ctest --test-dir build --output-on-failure` reported 1/1 passing; `py -3 -m pytest tests/python -q` reported 5/5 passing.
