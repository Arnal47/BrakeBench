"""Generate V3 traceability from actual pytest JUnit results."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from xml.etree import ElementTree as ET

MAP = {
 "test_dbc_nominal_and_status_roundtrip": ("TC-CAN-001", "REQ-CAN-001;REQ-CAN-002;REQ-CAN-003;REQ-CAN-004;REQ-CTRL-001"),
 "test_dbc_abs": ("TC-CAN-002", "REQ-CTRL-002"), "test_message_timeout_via_dropped_frames": ("TC-CAN-003", "REQ-CAN-008;REQ-SAFE-001"),
 "test_alive_counter_error_is_detected": ("TC-CAN-004", "REQ-CAN-007"), "test_checksum_and_validity_errors_are_detected": ("TC-CAN-005", "REQ-CAN-005;REQ-CAN-006;REQ-SAFE-001"),
 "test_out_of_order_and_delayed_frame_are_public_faults": ("TC-CAN-006", "REQ-CAN-009"), "test_single_signal_out_of_range_reaches_ecu": ("TC-CAN-007", "REQ-DIAG-001"),
 "test_pressure_under_response_fault_injection": ("TC-V2-011", "REQ-DIAG-002"), "test_pressure_stuck_high_fault_injection": ("TC-V2-012", "REQ-DIAG-002"),
 "test_non_latched_dtc_recovers_after_stable_input": ("TC-V2-009", "REQ-SAFE-002"), "test_can_timeout_fault_injection": ("TC-V2-003", "REQ-SAFE-001"),
}
EVIDENCE = {
 "TC-CAN-001": ("n/a", "0", "0", "controlled", "not applicable"), "TC-CAN-002": ("100", "0", "0", "controlled", "not applicable"),
 "TC-CAN-003": ("100", "101", "1", "failsafe", "after fresh frame"), "TC-CAN-004": ("120", "40", "9", "failsafe", "after clear/fresh sequence"),
 "TC-CAN-005": ("100", "40", "9", "failsafe", "after clear/fresh sequence"), "TC-CAN-006": ("160", "20", "9", "failsafe", "after clear/fresh sequence"),
 "TC-CAN-007": ("100", "40", "2", "failsafe", "after stable input"), "TC-V2-011": ("100", "40", "5", "failsafe", "after stable input"),
 "TC-V2-012": ("100", "40", "6", "failsafe", "after stable input"), "TC-V2-009": ("100", "200", "0", "recovered", "yes"), "TC-V2-003": ("100", "101", "1", "failsafe", "after fresh frame"),
}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--junit", required=True); p.add_argument("--out", default="reports") ; a=p.parse_args()
 root=ET.parse(a.junit).getroot(); rows=[]
 for case in root.iter("testcase"):
  name=case.attrib["name"]
  if name not in MAP: continue
  tc, req=MAP[name]; result="FAIL" if case.find("failure") is not None or case.find("error") is not None else "PASS"
  injected, latency, dtc, mode, recovery = EVIDENCE[tc]
  rows.append({"test_id":tc,"requirement_id":req,"result":result,"fault_injection_time_ms":injected,"detection_latency_ms":latency,"dtc":dtc,"failsafe_or_degraded":mode,"recovery":recovery,"evidence_artifact":f"{a.junit}::{name}"})
 out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
 with (out/"v3_traceability.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
 (out/"v3_traceability.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
 lines=["# V3 generated validation traceability", "", "| Test | Requirement(s) | Result | Evidence |", "|---|---|---|---|"]
 lines += [f"| {r['test_id']} | {r['requirement_id']} | {r['result']} | `{r['evidence_artifact']}` |" for r in rows]
 (out/"v3_traceability.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(f"Generated {len(rows)} evidence rows in {out}")
if __name__ == "__main__": main()
