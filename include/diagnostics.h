#ifndef DIAGNOSTICS_H
#define DIAGNOSTICS_H
#include "brake_ecu.h"
#define DIAG_CONFIRM_MS 40U
#define DIAG_RECOVERY_MS 100U
void diagnostics_init(Diagnostics *diagnostics);
void diagnostics_update(Diagnostics *diagnostics, const BrakeCanInput *input, uint32_t now_ms, uint32_t last_can_ms, bool has_input, uint16_t commanded_pressure);
const char *diagnostics_dtc_name(DtcCode code);
#endif
