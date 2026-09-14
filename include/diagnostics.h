#ifndef DIAGNOSTICS_H
#define DIAGNOSTICS_H
#include "brake_ecu.h"
BrakeFaultCode diagnostics_validate(const BrakeCanInput *input, uint32_t now_ms, uint32_t last_can_ms, bool has_input);
#endif
