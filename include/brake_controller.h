#ifndef BRAKE_CONTROLLER_H
#define BRAKE_CONTROLLER_H
#include "brake_ecu.h"
uint16_t brake_controller_pressure(uint16_t request_pct, bool abs_active);
bool brake_controller_abs_needed(const BrakeCanInput *input);
#endif
