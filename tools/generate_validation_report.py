"""Generate V3 traceability from actual pytest JUnit results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from xml.etree import ElementTree as ET


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--junit", required=True)
    p.add_argument("--ctest-junit", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--out", default="reports")
    a = p.parse_args()
    root = ET.parse(a.junit).getroot()
    outcomes = {
        case.attrib["name"]: "FAIL"
        if case.find("failure") is not None or case.find("error") is not None
        else "PASS"
        for case in root.iter("testcase")
    }
    rows = []
    evidence = json.loads(Path(a.evidence).read_text(encoding="utf-8"))
    test_names = {
        "TC-CAN-001": "test_dbc_nominal_and_status_roundtrip",
        "TC-CAN-002": "test_dbc_abs",
        "TC-CAN-003": "test_message_timeout_via_dropped_frames",
        "TC-CAN-004": "test_alive_counter_error_is_detected",
        "TC-CAN-005": "test_checksum_error_is_detected",
        "TC-CAN-006": "test_validity_zero_is_detected_independently",
        "TC-CAN-007": "test_out_of_order_and_delayed_frame_are_public_faults",
        "TC-CAN-008": "test_single_signal_out_of_range_reaches_ecu",
        "TC-CAN-009": "test_dbc_contract_ids_cycles_and_signal_metadata",
        "TC-V2-001": "test_nominal_braking",
        "TC-V2-002": "test_abs_intervention",
        "TC-V2-003": "test_can_timeout_fault_injection",
        "TC-V2-004": "test_overpressure_fault_injection",
        "TC-V2-005": "test_invalid_wheel_speed_fault_injection",
        "TC-V2-006": "test_timeout_reports_dtc_and_failsafe",
        "TC-V2-007": "test_wheel_stuck_degrades_without_failsafe",
        "TC-V2-008": "test_wheel_mismatch_degrades",
        "TC-V2-009": "test_non_latched_dtc_recovers_after_stable_input",
        "TC-V2-010": "test_corrupt_message_fault_injection",
        "TC-V2-011": "test_pressure_under_response_fault_injection",
        "TC-V2-012": "test_pressure_stuck_high_fault_injection",
        "TC-V2-013": "test_pressure_stuck_low_fault_injection",
    }
    for record in evidence:
        test_name = test_names[record["test_id"]]
        record["result"] = outcomes[test_name]
        record["fault_injection_time_ms"] = record.pop("injected_at_ms")
        detected = record.pop("detected_at_ms")
        record["detection_latency_ms"] = (
            None
            if detected is None or record["fault_injection_time_ms"] is None
            else detected - record["fault_injection_time_ms"]
        )
        record["failsafe_or_degraded"] = (
            "failsafe" if record.pop("failsafe") else "degraded_or_controlled"
        )
        record["evidence_artifact"] = record.pop("artifact")
        rows.append(record)
    ctest_root = ET.parse(a.ctest_junit).getroot()
    ctest_case = next(
        case
        for case in ctest_root.iter("testcase")
        if case.attrib["name"] == "ecu_unit_tests"
    )
    ctest_result = "FAIL" if ctest_case.find("failure") is not None else "PASS"
    rows.append(
        {
            "test_id": "TC-V2-C-001",
            "requirement_id": "REQ-DIAG-003",
            "result": ctest_result,
            "dtc": "public C API clear verification",
            "recovery": "latched DTC clear",
            "fault_injection_time_ms": None,
            "detection_latency_ms": None,
            "failsafe_or_degraded": "C unit test",
            "evidence_artifact": f"{a.ctest_junit}::ecu_unit_tests",
        }
    )
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "v3_traceability.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    (out / "v3_traceability.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    lines = [
        "# V3 generated validation traceability",
        "",
        "| Test | Requirement(s) | Result | Evidence |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| {r['test_id']} | {r['requirement_id']} | {r['result']} | `{r['evidence_artifact']}` |"
        for r in rows
    ]
    (out / "v3_traceability.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(rows)} evidence rows in {out}")


if __name__ == "__main__":
    main()
